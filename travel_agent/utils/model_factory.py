"""
Model Factory - 统一的LLM模型创建工具
提供统一的ModelScope模型创建逻辑，避免重复代码
"""

import os
import time
import logging
from typing import Optional
from google.adk.models.lite_llm import LiteLlm

logger = logging.getLogger(__name__)

class ModelFactory:
    """统一的LLM模型工厂类"""
    
    # 全局模型配置
    MODELS_TO_TRY = [
        "Qwen/Qwen3-235B-A22B",
        "deepseek-ai/DeepSeek-V3.1", 
        "deepseek-ai/DeepSeek-R1-0528"
    ]
    
    API_BASE = "https://api-inference.modelscope.cn/v1"
    CUSTOM_LLM_PROVIDER = "openai"
    MAX_RETRIES = 2
    TIMEOUT = 30
    RETRY_DELAY = 2  # seconds
    
    @classmethod
    def create_llm_model(cls, service_name: str = "Unknown") -> Optional[LiteLlm]:
        """
        创建LiteLLM模型，带有完整的错误处理和重试逻辑
        
        Args:
            service_name: 调用服务的名称，用于日志记录
            
        Returns:
            LiteLlm实例或None（如果所有模型都失败）
        """
        try:
            # 获取API密钥
            api_key = cls._get_api_key()
            
            # 尝试每个模型
            for i, model in enumerate(cls.MODELS_TO_TRY):
                try:
                    logger.info(f"[{service_name}] Attempting to create model: {model} (attempt {i+1}/{len(cls.MODELS_TO_TRY)})")
                    
                    # 配置模型参数
                    model_kwargs = cls._get_model_kwargs(model, api_key)
                    
                    # 创建模型
                    llm_model = LiteLlm(**model_kwargs)
                    
                    logger.info(f"[{service_name}] ✅ Successfully created model: {model}")
                    return llm_model
                    
                except Exception as e:
                    logger.error(f"[{service_name}] ❌ Failed to create model {model}: {str(e)[:100]}...")
                    
                    # 如果不是最后一个模型，等待后重试
                    if model != cls.MODELS_TO_TRY[-1]:
                        logger.info(f"[{service_name}] ⏭️  Trying next model in {cls.RETRY_DELAY}s...")
                        time.sleep(cls.RETRY_DELAY)
                    continue
            
            # 所有模型都失败
            logger.warning(f"[{service_name}] ❌ All model options failed. AI enhancement will be limited.")
            return None
            
        except Exception as e:
            logger.error(f"[{service_name}] ❌ Critical error in model creation: {str(e)}")
            return None
    
    @classmethod
    def _get_api_key(cls) -> str:
        """获取API密钥"""
        api_key = os.getenv("MODELSCOPE_API_KEY") or "dummy_key"
        if not os.getenv("MODELSCOPE_API_KEY"):
            logger.warning("MODELSCOPE_API_KEY not found, using dummy key for ModelScope")
        return api_key
    
    @classmethod
    def _get_model_kwargs(cls, model: str, api_key: str) -> dict:
        """获取模型配置参数"""
        model_kwargs = {
            "model": model,
            "api_key": api_key,
            "api_base": cls.API_BASE,
            "custom_llm_provider": cls.CUSTOM_LLM_PROVIDER,
            "max_retries": cls.MAX_RETRIES,
            "timeout": cls.TIMEOUT
        }
        
        # Qwen模型的特殊配置
        if "Qwen" in model:
            logger.info(f"🔧 Configuring Qwen model {model} with enable_thinking=false")
            model_kwargs["enable_thinking"] = False
        
        return model_kwargs
    
    @classmethod
    def create_model_with_fallback(cls, service_name: str = "Unknown") -> LiteLlm:
        """
        创建模型，如果失败则抛出异常（用于必须有模型的场景）
        
        Args:
            service_name: 调用服务的名称
            
        Returns:
            LiteLlm实例
            
        Raises:
            RuntimeError: 如果所有模型都失败
        """
        model = cls.create_llm_model(service_name)
        if model is None:
            raise RuntimeError(f"[{service_name}] All model options failed. Please check your API key and try again later.")
        return model

# 便捷函数，用于向后兼容
def create_llm_model(service_name: str = "Unknown") -> Optional[LiteLlm]:
    """便捷函数：创建LLM模型"""
    return ModelFactory.create_llm_model(service_name)

def create_model_with_fallback(service_name: str = "Unknown") -> LiteLlm:
    """便捷函数：创建模型（失败时抛出异常）"""
    return ModelFactory.create_model_with_fallback(service_name)
