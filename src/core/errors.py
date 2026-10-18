"""
Error handling and recovery system.

Implements structured error classification, recovery strategies,
and human/agent-facing error messages.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


class ErrorSeverity(Enum):
    """Error severity levels."""
    P0 = "critical"      # System-breaking, immediate action required
    P1 = "high"          # Major functionality impaired
    P2 = "medium"        # Minor functionality impaired
    P3 = "low"           # Cosmetic or edge case


class ErrorRecoverability(Enum):
    """Error recoverability types."""
    TRANSIENT = "transient"        # Temporary, retry may succeed
    PERMANENT = "permanent"        # Permanent, requires manual intervention
    AMBIGUOUS = "ambiguous"        # Unknown, needs investigation


class ErrorCategory(Enum):
    """Error categories."""
    PROVIDER = "provider"          # LLM provider errors
    STORAGE = "storage"            # Storage/filesystem errors
    NETWORK = "network"            # Network/connectivity errors
    VALIDATION = "validation"      # Input validation errors
    CONFIGURATION = "configuration"  # Configuration errors
    AGENT = "agent"                # Agent execution errors
    WORKFLOW = "workflow"          # Workflow orchestration errors
    SYSTEM = "system"              # System-level errors


@dataclass
class ErrorContext:
    """Context information for an error."""
    request_id: Optional[str] = None
    agent_type: Optional[str] = None
    workflow_step: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StructuredError:
    """Structured error with classification and recovery information."""
    
    # Error identification
    error_code: str
    category: ErrorCategory
    severity: ErrorSeverity
    recoverability: ErrorRecoverability
    
    # Error details
    message: str
    technical_details: str
    context: ErrorContext
    
    # Recovery information
    recovery_suggestions: List[str] = field(default_factory=list)
    retry_after_seconds: Optional[int] = None
    
    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage."""
        return {
            "error_code": self.error_code,
            "category": self.category.value,
            "severity": self.severity.value,
            "recoverability": self.recoverability.value,
            "message": self.message,
            "technical_details": self.technical_details,
            "context": {
                "request_id": self.context.request_id,
                "agent_type": self.context.agent_type,
                "workflow_step": self.context.workflow_step,
                "provider": self.context.provider,
                "model": self.context.model,
                "metadata": self.context.metadata
            },
            "recovery_suggestions": self.recovery_suggestions,
            "retry_after_seconds": self.retry_after_seconds,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id
        }
    
    def get_human_message(self) -> str:
        """Get human-friendly error message."""
        parts = [f"Error: {self.message}"]
        
        if self.recovery_suggestions:
            parts.append("\nWhat you can do:")
            for i, suggestion in enumerate(self.recovery_suggestions, 1):
                parts.append(f"  {i}. {suggestion}")
        
        if self.retry_after_seconds:
            parts.append(f"\nYou can retry in {self.retry_after_seconds} seconds.")
        
        return "\n".join(parts)
    
    def get_agent_message(self) -> str:
        """Get agent-friendly error message (abbreviated)."""
        parts = [
            f"err:{self.error_code}",
            f"cat:{self.category.value}",
            f"sev:{self.severity.value}",
            f"rec:{self.recoverability.value}"
        ]
        
        if self.retry_after_seconds:
            parts.append(f"retry:{self.retry_after_seconds}s")
        
        return " ".join(parts)


class ErrorClassifier:
    """Classifies errors and provides recovery strategies."""
    
    # Error code definitions
    ERROR_CODES = {
        # Provider errors (PRV-xxx)
        "PRV-001": {
            "message": "API key not found or invalid",
            "category": ErrorCategory.PROVIDER,
            "severity": ErrorSeverity.P0,
            "recoverability": ErrorRecoverability.PERMANENT,
            "suggestions": [
                "Check that your API key is set in environment variables",
                "Verify the API key is valid and not expired",
                "Ensure the correct environment variable name is used"
            ]
        },
        "PRV-002": {
            "message": "Rate limit exceeded",
            "category": ErrorCategory.PROVIDER,
            "severity": ErrorSeverity.P1,
            "recoverability": ErrorRecoverability.TRANSIENT,
            "retry_after": 60,
            "suggestions": [
                "Wait a moment and try again",
                "Reduce the number of concurrent requests",
                "Consider upgrading your API plan"
            ]
        },
        "PRV-003": {
            "message": "Model not available",
            "category": ErrorCategory.PROVIDER,
            "severity": ErrorSeverity.P1,
            "recoverability": ErrorRecoverability.PERMANENT,
            "suggestions": [
                "Check that the model name is correct in configuration",
                "Verify you have access to this model",
                "Try using a different model"
            ]
        },
        "PRV-004": {
            "message": "Token limit exceeded",
            "category": ErrorCategory.PROVIDER,
            "severity": ErrorSeverity.P2,
            "recoverability": ErrorRecoverability.PERMANENT,
            "suggestions": [
                "Reduce the input size or context",
                "Use a model with larger context window",
                "Split the task into smaller chunks"
            ]
        },
        "PRV-005": {
            "message": "Provider service unavailable",
            "category": ErrorCategory.PROVIDER,
            "severity": ErrorSeverity.P1,
            "recoverability": ErrorRecoverability.TRANSIENT,
            "retry_after": 300,
            "suggestions": [
                "Wait a few minutes and try again",
                "Check provider status page",
                "Try using a different provider"
            ]
        },
        
        # Storage errors (STR-xxx)
        "STR-001": {
            "message": "Document not found",
            "category": ErrorCategory.STORAGE,
            "severity": ErrorSeverity.P2,
            "recoverability": ErrorRecoverability.PERMANENT,
            "suggestions": [
                "Verify the document ID is correct",
                "Check if the document was deleted",
                "List available documents to find the correct ID"
            ]
        },
        "STR-002": {
            "message": "Storage path not accessible",
            "category": ErrorCategory.STORAGE,
            "severity": ErrorSeverity.P0,
            "recoverability": ErrorRecoverability.PERMANENT,
            "suggestions": [
                "Check that the storage directory exists",
                "Verify you have write permissions",
                "Run 'ucas init' to create required directories"
            ]
        },
        "STR-003": {
            "message": "Disk space insufficient",
            "category": ErrorCategory.STORAGE,
            "severity": ErrorSeverity.P1,
            "recoverability": ErrorRecoverability.PERMANENT,
            "suggestions": [
                "Free up disk space",
                "Delete old documents or archives",
                "Change storage path to a location with more space"
            ]
        },
        
        # Network errors (NET-xxx)
        "NET-001": {
            "message": "Network connection failed",
            "category": ErrorCategory.NETWORK,
            "severity": ErrorSeverity.P1,
            "recoverability": ErrorRecoverability.TRANSIENT,
            "retry_after": 30,
            "suggestions": [
                "Check your internet connection",
                "Verify firewall settings",
                "Try again in a moment"
            ]
        },
        "NET-002": {
            "message": "Request timeout",
            "category": ErrorCategory.NETWORK,
            "severity": ErrorSeverity.P2,
            "recoverability": ErrorRecoverability.TRANSIENT,
            "retry_after": 60,
            "suggestions": [
                "Check your network connection",
                "The request may be too large, try reducing it",
                "Try again with a longer timeout"
            ]
        },
        
        # Validation errors (VAL-xxx)
        "VAL-001": {
            "message": "Invalid input format",
            "category": ErrorCategory.VALIDATION,
            "severity": ErrorSeverity.P2,
            "recoverability": ErrorRecoverability.PERMANENT,
            "suggestions": [
                "Check the input format matches requirements",
                "Review the documentation for correct format",
                "Provide all required fields"
            ]
        },
        "VAL-002": {
            "message": "Required parameter missing",
            "category": ErrorCategory.VALIDATION,
            "severity": ErrorSeverity.P2,
            "recoverability": ErrorRecoverability.PERMANENT,
            "suggestions": [
                "Provide all required parameters",
                "Check the documentation for required fields",
                "Use --help to see available options"
            ]
        },
        
        # Configuration errors (CFG-xxx)
        "CFG-001": {
            "message": "Configuration file not found",
            "category": ErrorCategory.CONFIGURATION,
            "severity": ErrorSeverity.P1,
            "recoverability": ErrorRecoverability.PERMANENT,
            "suggestions": [
                "Run 'ucas init' to create default configuration",
                "Check that config/default.yaml exists",
                "Restore configuration from backup"
            ]
        },
        "CFG-002": {
            "message": "Invalid configuration format",
            "category": ErrorCategory.CONFIGURATION,
            "severity": ErrorSeverity.P1,
            "recoverability": ErrorRecoverability.PERMANENT,
            "suggestions": [
                "Check YAML syntax in configuration file",
                "Restore default configuration",
                "Review configuration documentation"
            ]
        },
        "CFG-003": {
            "message": "Provider not enabled",
            "category": ErrorCategory.CONFIGURATION,
            "severity": ErrorSeverity.P2,
            "recoverability": ErrorRecoverability.PERMANENT,
            "suggestions": [
                "Enable the provider in config/default.yaml",
                "Set 'enabled: true' for the provider",
                "Verify API key is configured"
            ]
        },
        
        # Agent errors (AGT-xxx)
        "AGT-001": {
            "message": "Agent execution failed",
            "category": ErrorCategory.AGENT,
            "severity": ErrorSeverity.P1,
            "recoverability": ErrorRecoverability.AMBIGUOUS,
            "suggestions": [
                "Check the error details for specific cause",
                "Verify input is valid",
                "Try again or contact support"
            ]
        },
        "AGT-002": {
            "message": "Agent timeout",
            "category": ErrorCategory.AGENT,
            "severity": ErrorSeverity.P2,
            "recoverability": ErrorRecoverability.TRANSIENT,
            "retry_after": 60,
            "suggestions": [
                "The task may be too complex, try simplifying",
                "Increase timeout in configuration",
                "Try again with a faster model"
            ]
        },
        
        # Workflow errors (WFL-xxx)
        "WFL-001": {
            "message": "Workflow not found",
            "category": ErrorCategory.WORKFLOW,
            "severity": ErrorSeverity.P2,
            "recoverability": ErrorRecoverability.PERMANENT,
            "suggestions": [
                "Check that the content type is valid",
                "Use 'ucas workflows' to see available workflows",
                "Specify a different content type"
            ]
        },
        "WFL-002": {
            "message": "Workflow step failed",
            "category": ErrorCategory.WORKFLOW,
            "severity": ErrorSeverity.P1,
            "recoverability": ErrorRecoverability.AMBIGUOUS,
            "suggestions": [
                "Check the error details for the failed step",
                "Review previous step outputs",
                "Try restarting the workflow"
            ]
        },
    }
    
    @classmethod
    def classify_error(
        cls,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> StructuredError:
        """Classify an error and return structured error information.
        
        Args:
            error: The exception to classify
            context: Optional context information
            
        Returns:
            StructuredError with classification and recovery info
        """
        error_str = str(error).lower()
        context = context or ErrorContext()
        
        # Try to match error to known patterns
        error_code = cls._match_error_code(error_str, error)
        
        if error_code and error_code in cls.ERROR_CODES:
            error_def = cls.ERROR_CODES[error_code]
            return StructuredError(
                error_code=error_code,
                category=error_def["category"],
                severity=error_def["severity"],
                recoverability=error_def["recoverability"],
                message=error_def["message"],
                technical_details=str(error),
                context=context,
                recovery_suggestions=error_def.get("suggestions", []),
                retry_after_seconds=error_def.get("retry_after")
            )
        
        # Unknown error - classify as ambiguous
        return StructuredError(
            error_code="UNK-001",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.P2,
            recoverability=ErrorRecoverability.AMBIGUOUS,
            message="An unexpected error occurred",
            technical_details=str(error),
            context=context,
            recovery_suggestions=[
                "Check the error details",
                "Try the operation again",
                "Contact support if the issue persists"
            ]
        )
    
    @classmethod
    def _match_error_code(cls, error_str: str, error: Exception) -> Optional[str]:
        """Match error string to error code."""
        # API key errors
        if any(x in error_str for x in ["api key", "api_key", "authentication", "unauthorized"]):
            return "PRV-001"
        
        # Rate limit errors
        if any(x in error_str for x in ["rate limit", "too many requests", "429"]):
            return "PRV-002"
        
        # Model errors
        if any(x in error_str for x in ["model not found", "invalid model", "model unavailable"]):
            return "PRV-003"
        
        # Token limit errors
        if any(x in error_str for x in ["token limit", "context length", "too long"]):
            return "PRV-004"
        
        # Service unavailable
        if any(x in error_str for x in ["service unavailable", "503", "502", "500"]):
            return "PRV-005"
        
        # Storage errors
        if any(x in error_str for x in ["file not found", "document not found", "no such file"]):
            return "STR-001"
        
        if any(x in error_str for x in ["permission denied", "access denied", "not accessible"]):
            return "STR-002"
        
        if any(x in error_str for x in ["disk full", "no space", "insufficient space"]):
            return "STR-003"
        
        # Network errors
        if any(x in error_str for x in ["connection", "network", "unreachable"]):
            return "NET-001"
        
        if "timeout" in error_str:
            return "NET-002"
        
        # Configuration errors
        if any(x in error_str for x in ["config", "configuration"]):
            if "not found" in error_str:
                return "CFG-001"
            elif any(x in error_str for x in ["invalid", "parse", "yaml"]):
                return "CFG-002"
            elif "not enabled" in error_str:
                return "CFG-003"
        
        # Workflow errors
        if "workflow" in error_str:
            if "not found" in error_str:
                return "WFL-001"
            else:
                return "WFL-002"
        
        return None


class ErrorRecovery:
    """Handles error recovery strategies."""
    
    @staticmethod
    def should_retry(error: StructuredError) -> bool:
        """Determine if operation should be retried.
        
        Args:
            error: Structured error
            
        Returns:
            True if retry is recommended
        """
        return error.recoverability == ErrorRecoverability.TRANSIENT
    
    @staticmethod
    def get_retry_delay(error: StructuredError) -> int:
        """Get recommended retry delay in seconds.
        
        Args:
            error: Structured error
            
        Returns:
            Delay in seconds
        """
        if error.retry_after_seconds:
            return error.retry_after_seconds
        
        # Default delays based on severity
        if error.severity == ErrorSeverity.P0:
            return 0  # Immediate retry not recommended
        elif error.severity == ErrorSeverity.P1:
            return 60
        elif error.severity == ErrorSeverity.P2:
            return 30
        else:
            return 10
    
    @staticmethod
    def get_max_retries(error: StructuredError) -> int:
        """Get maximum number of retries.
        
        Args:
            error: Structured error
            
        Returns:
            Maximum retry attempts
        """
        if error.recoverability == ErrorRecoverability.PERMANENT:
            return 0
        elif error.recoverability == ErrorRecoverability.TRANSIENT:
            return 3
        else:  # AMBIGUOUS
            return 1
