"""Translation service module."""

from typing import Optional, Callable
from PyQt5.QtCore import QThread, pyqtSignal

import openai

from core.logger import get_logger
from core.types import TranslationRequest, TranslationResult
from models.cache_manager import CacheManager

logger = get_logger("TranslationService")


class TranslationWorker(QThread):
    """翻译工作线程。"""
    
    result_ready = pyqtSignal(str)  # 发送翻译结果（包括中间结果）
    finished_signal = pyqtSignal(TranslationResult)  # 发送最终结果
    
    def __init__(
        self,
        request: TranslationRequest,
        cache: Optional[CacheManager] = None,
    ):
        super().__init__()
        self._request = request
        self._cache = cache
    
    def run(self) -> None:
        """执行翻译任务。"""
        try:
            # 检查是否被请求中断
            if self.isInterruptionRequested():
                return
            
            # 检查缓存
            if self._cache:
                cached = self._cache.get(self._request.text, min_gap=3.0)
                if cached:
                    self.result_ready.emit(cached)
                    self.finished_signal.emit(TranslationResult(
                        success=True,
                        content=cached,
                        from_cache=True,
                    ))
                    return
            
            # 验证API配置
            if not self._request.api_key:
                error = "API密钥未设置，请在设置中配置API。"
                self.result_ready.emit(f"@An error occurred:{error}\n ")
                self.finished_signal.emit(TranslationResult(
                    success=False,
                    content="",
                    error=error,
                ))
                return
            
            if not self._request.base_url:
                error = "API基础URL未设置，请在设置中配置。"
                self.result_ready.emit(f"@An error occurred:{error}\n ")
                self.finished_signal.emit(TranslationResult(
                    success=False,
                    content="",
                    error=error,
                ))
                return
            
            # 确保base_url以斜杠结尾
            base_url = self._request.base_url
            if not base_url.endswith('/'):
                base_url += '/'
            
            # 格式化提示词（同时提供 text 和 selected_text 以兼容不同模板）
            prompt = self._request.prompt_template.format(
                text=self._request.text,
                selected_text=self._request.text,
                source_language=self._request.source_language.native,
                source_language_en=self._request.source_language.code,
                target_language=self._request.target_language.native,
                target_language_en=self._request.target_language.code,
            )
            
            # 创建 OpenAI 客户端并请求API
            client = openai.OpenAI(api_key=self._request.api_key, base_url=base_url)
            completion_stream = client.chat.completions.create(
                model=self._request.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )
            
            response_content = ""
            chunk_count = 0
            
            for chunk in completion_stream:
                # 检查是否被请求中断
                if self.isInterruptionRequested():
                    logger.info("翻译线程收到中断请求，正在停止...")
                    return
                
                try:
                    content = chunk.choices[0].delta.content or ""
                    response_content += content
                    
                    # 控制发送频率，前3次每次都发，之后每3次发一次
                    if chunk_count < 3 or chunk_count % 3 == 0:
                        self.result_ready.emit(response_content)
                    chunk_count += 1
                except Exception as e:
                    logger.error(f"处理chunk时出错: {e}")
            
            # 发送最终结果
            logger.info(f"翻译完成，共 {len(response_content)} 字符")
            self.result_ready.emit(response_content)
            
            # 保存到缓存
            if self._cache:
                self._cache.set(self._request.text, response_content)
            
            self.finished_signal.emit(TranslationResult(
                success=True,
                content=response_content,
            ))
            
        except Exception as e:
            # 只有在非主动中断的情况下才报错
            if not self.isInterruptionRequested():
                error_msg = str(e)
                logger.error(f"翻译错误: {error_msg}")
                self.result_ready.emit(f"@An error occurred:{error_msg}\n ")
                self.finished_signal.emit(TranslationResult(
                    success=False,
                    content="",
                    error=error_msg,
                ))


class TranslationService:
    """翻译服务，管理翻译任务的生命周期。"""
    
    def __init__(self, cache: Optional[CacheManager] = None):
        """
        初始化翻译服务。
        
        Args:
            cache: 缓存管理器实例
        """
        self._cache = cache
        self._current_worker: Optional[TranslationWorker] = None
    
    def translate(
        self,
        request: TranslationRequest,
        on_progress: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[TranslationResult], None]] = None,
    ) -> TranslationWorker:
        """
        开始翻译任务。
        
        Args:
            request: 翻译请求
            on_progress: 进度回调，接收中间翻译结果
            on_complete: 完成回调，接收最终翻译结果
            
        Returns:
            翻译工作线程
        """
        # 取消之前的翻译
        self.cancel()
        
        # 创建新的工作线程
        worker = TranslationWorker(request, self._cache)
        
        if on_progress:
            worker.result_ready.connect(on_progress)
        if on_complete:
            worker.finished_signal.connect(on_complete)
        
        self._current_worker = worker
        worker.start()
        
        return worker
    
    def cancel(self) -> None:
        """取消当前翻译任务。"""
        if self._current_worker and self._current_worker.isRunning():
            try:
                # 请求中断
                self._current_worker.requestInterruption()
                self._current_worker.wait(500)
                
                # 如果仍在运行，强制终止
                if self._current_worker.isRunning():
                    logger.warning("线程未响应中断请求，强制终止...")
                    self._current_worker.terminate()
                    self._current_worker.wait(200)
                
                # 断开信号连接
                try:
                    self._current_worker.result_ready.disconnect()
                except TypeError:
                    pass
                try:
                    self._current_worker.finished_signal.disconnect()
                except TypeError:
                    pass
                    
            except Exception as e:
                logger.error(f"取消翻译任务时出错: {e}")
            finally:
                self._current_worker = None
    
    @property
    def is_running(self) -> bool:
        """检查是否有翻译任务正在运行。"""
        return self._current_worker is not None and self._current_worker.isRunning()
