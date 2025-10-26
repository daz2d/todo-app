"""
LLM Provider Abstraction

Provides unified interface for different LLM providers (Ollama, OpenAI, Together AI, Hugging Face).
Supports easy switching via environment configuration.
"""

import os
from typing import Optional
try:
    # Try new langchain-ollama package first (LangChain 0.3.1+)
    from langchain_ollama import ChatOllama
except ImportError:
    # Fall back to legacy import
    from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel


def get_chat_model(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    **kwargs
) -> BaseChatModel:
    """
    Get a chat model based on provider configuration.
    
    Args:
        provider: LLM provider name ('ollama', 'openai', 'together', 'hf').
                 Defaults to LLM_PROVIDER env var or 'ollama'.
        model: Model name (provider-specific).
               Defaults to LLM_MODEL env var or 'codellama:latest'.
        temperature: Generation temperature (0.0-1.0).
                    Defaults to LLM_TEMPERATURE env var or 0.2.
        **kwargs: Additional provider-specific parameters.
    
    Returns:
        Configured chat model instance.
    
    Raises:
        ValueError: If provider is unsupported or configuration is invalid.
        ImportError: If required provider client library is not installed.
    
    Examples:
        >>> # Use default Ollama
        >>> model = get_chat_model()
        
        >>> # Use specific provider and model
        >>> model = get_chat_model(provider='ollama', model='codellama:13b')
        
        >>> # Override temperature
        >>> model = get_chat_model(temperature=0.5)
    """
    # Load configuration from environment
    provider = provider or os.getenv('LLM_PROVIDER', 'ollama')
    model = model or os.getenv('LLM_MODEL', 'codellama:latest')
    temperature = temperature if temperature is not None else float(os.getenv('LLM_TEMPERATURE', '0.2'))
    
    provider = provider.lower().strip()
    
    # Ollama (default, local)
    if provider == 'ollama':
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        max_retries = int(os.getenv('MAX_RETRIES', '3'))
        
        return ChatOllama(
            model=model,
            base_url=base_url,
            temperature=temperature,
            num_predict=int(os.getenv('MAX_TOKENS', '0')) or None,
            **kwargs
        )
    
    # Together AI (cloud)
    elif provider == 'together':
        try:
            from langchain_community.chat_models import ChatTogether
        except ImportError:
            raise ImportError(
                "Together AI support requires 'together' package. "
                "Install with: pip install together"
            )
        
        api_key = os.getenv('TOGETHER_API_KEY')
        if not api_key:
            raise ValueError(
                "TOGETHER_API_KEY environment variable is required for Together AI provider. "
                "Get your API key from https://together.ai"
            )
        
        return ChatTogether(
            model=model,
            together_api_key=api_key,
            temperature=temperature,
            max_tokens=int(os.getenv('MAX_TOKENS', '0')) or None,
            **kwargs
        )
    
    # OpenAI (cloud)
    elif provider == 'openai':
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError(
                "OpenAI support requires 'langchain-openai' package. "
                "Install with: pip install langchain-openai"
            )
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required for OpenAI provider. "
                "Get your API key from https://platform.openai.com/api-keys"
            )
        
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=int(os.getenv('MAX_TOKENS', '0')) or None,
            **kwargs
        )
    
    # Hugging Face (cloud)
    elif provider in ('hf', 'huggingface'):
        try:
            from langchain_community.chat_models import ChatHuggingFace
            from langchain_community.llms import HuggingFaceHub
        except ImportError:
            raise ImportError(
                "Hugging Face support requires 'huggingface_hub' package. "
                "Install with: pip install huggingface_hub"
            )
        
        api_token = os.getenv('HF_API_TOKEN')
        if not api_token:
            raise ValueError(
                "HF_API_TOKEN environment variable is required for Hugging Face provider. "
                "Get your token from https://huggingface.co/settings/tokens"
            )
        
        llm = HuggingFaceHub(
            repo_id=model,
            huggingfacehub_api_token=api_token,
            model_kwargs={
                "temperature": temperature,
                "max_new_tokens": int(os.getenv('MAX_TOKENS', '512')),
            }
        )
        
        return ChatHuggingFace(llm=llm, **kwargs)
    
    # Unsupported provider
    else:
        raise ValueError(
            f"Unsupported LLM provider: '{provider}'. "
            f"Supported providers: 'ollama', 'openai', 'together', 'hf'. "
            f"Update LLM_PROVIDER in your .env file."
        )


def get_smart_model(needs_tools: bool = False, **kwargs) -> BaseChatModel:
    """
    Get the appropriate model based on whether tools are needed.
    
    This enables hybrid deployments where:
    - Tool-requiring agents use powerful cloud models (OpenAI)
    - Non-tool agents use fast local models (Ollama)
    
    Args:
        needs_tools: If True, returns a model capable of tool calling.
                    If False, returns a lightweight model for text generation.
        **kwargs: Additional provider-specific parameters.
    
    Returns:
        Configured chat model instance.
    
    Environment Variables:
        LLM_PROVIDER_TOOLS: Provider for tool-capable tasks (default: 'openai')
        LLM_MODEL_TOOLS: Model for tool-capable tasks (default: 'gpt-4o-mini')
        LLM_PROVIDER_TEXT: Provider for text-only tasks (default: 'ollama')
        LLM_MODEL_TEXT: Model for text-only tasks (default: 'llama3.2:latest')
    
    Examples:
        >>> # For PM or Reviewer (no tools needed)
        >>> model = get_smart_model(needs_tools=False)
        
        >>> # For Backend or Frontend (tools needed)
        >>> model = get_smart_model(needs_tools=True)
    """
    if needs_tools:
        # Use tool-capable provider (typically cloud)
        provider = os.getenv('LLM_PROVIDER_TOOLS', os.getenv('LLM_PROVIDER', 'openai'))
        model = os.getenv('LLM_MODEL_TOOLS', 'gpt-4o-mini')
        print(f"🔧 Using tool-capable model: {provider}/{model}")
    else:
        # Use text-only provider (typically local/fast)
        provider = os.getenv('LLM_PROVIDER_TEXT', os.getenv('LLM_PROVIDER', 'ollama'))
        model = os.getenv('LLM_MODEL_TEXT', 'llama3.2:latest')
        print(f"💬 Using text-only model: {provider}/{model}")
    
    return get_chat_model(provider=provider, model=model, **kwargs)


def test_model_connection(model: Optional[BaseChatModel] = None) -> bool:
    """
    Test connection to LLM provider.
    
    Args:
        model: Chat model instance to test. If None, creates default model.
    
    Returns:
        True if connection successful, False otherwise.
    
    Examples:
        >>> model = get_chat_model()
        >>> if test_model_connection(model):
        ...     print("Model is ready!")
    """
    try:
        if model is None:
            model = get_chat_model()
        
        # Simple test query
        response = model.invoke([{"role": "user", "content": "Hi"}])
        return bool(response and response.content)
    
    except Exception as e:
        print(f"Model connection test failed: {e}")
        return False


# Extensibility: Add new providers by implementing provider-specific logic above
# Example structure for new provider:
#
# elif provider == 'your_provider':
#     try:
#         from langchain_community.chat_models import ChatYourProvider
#     except ImportError:
#         raise ImportError("Install with: pip install your-provider-sdk")
#     
#     api_key = os.getenv('YOUR_PROVIDER_API_KEY')
#     if not api_key:
#         raise ValueError("YOUR_PROVIDER_API_KEY required")
#     
#     return ChatYourProvider(
#         model=model,
#         api_key=api_key,
#         temperature=temperature,
#         **kwargs
#     )
