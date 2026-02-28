#!/usr/bin/env python3
"""
Smart Model Router for NEMO
Routes tasks to cheapest capable model: LM Studio (free) -> Kimi ($0.004) -> Opus ($$$)
"""

import os
import sys
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime

# Cost tracking log
COST_LOG = "/Users/symbiote_home/.nemo/workspace/cost-savings.log"

class SmartRouter:
    """Intelligent model routing to minimize costs."""
    
    def __init__(self):
        self.lm_studio_url = "http://localhost:1234/v1"
        self.models = {
            "local": {"name": "LM Studio (Mistral 7B)", "cost_per_1k": 0.0, "max_tokens": 8000},
            "kimi": {"name": "Kimi K2.5", "cost_per_1k": 0.0006, "max_tokens": 128000},
            "opus": {"name": "Claude Opus", "cost_per_1k": 0.015, "max_tokens": 200000}
        }
        self.savings = {"local": 0, "kimi": 0, "opus": 0, "saved": 0.0}
    
    def check_local_available(self) -> bool:
        """Check if LM Studio is running with a loaded model."""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.lm_studio_url}/models")
            with urllib.request.urlopen(req, timeout=2) as response:
                data = json.loads(response.read())
                return len(data.get("data", [])) > 0
        except:
            return False
    
    def analyze_task(self, prompt: str, context: str = "") -> Dict[str, Any]:
        """Analyze task complexity to determine best model."""
        full_input = prompt + context
        estimated_tokens = len(full_input) // 4  # Rough estimate: 4 chars = 1 token
        
        analysis = {
            "estimated_tokens": estimated_tokens,
            "complexity": "low",
            "speed_critical": False,
            "security_critical": False,
            "recommended_model": "local"
        }
        
        # Check complexity indicators
        complexity_markers = [
            "security", "audit", "vulnerability", "exploit", "breach",
            "strategy", "architecture", "design decision",
            "trading", "financial", "risk assessment",
            "complex", "multi-step", "reasoning chain"
        ]
        
        if any(marker in prompt.lower() for marker in complexity_markers):
            analysis["complexity"] = "high"
            analysis["recommended_model"] = "kimi"  # Default to Kimi for complex tasks
        
        # Check for security keywords
        security_markers = ["security", "audit", "key", "password", "credential", "private key"]
        if any(marker in prompt.lower() for marker in security_markers):
            analysis["security_critical"] = True
            analysis["recommended_model"] = "opus"
            return analysis
        
        # Check token count
        if estimated_tokens > 6000:
            analysis["recommended_model"] = "kimi"
        elif estimated_tokens > 8000:
            analysis["recommended_model"] = "kimi"  # Local max is ~8K
        
        # Check for speed requirements (interactive)
        speed_markers = ["quick", "fast", "now", "immediate", "waiting"]
        if any(marker in prompt.lower() for marker in speed_markers):
            analysis["speed_critical"] = True
            if analysis["complexity"] == "high":
                analysis["recommended_model"] = "kimi"
        
        return analysis
    
    def call_local(self, prompt: str, max_tokens: int = 500, timeout: int = 10) -> Optional[str]:
        """Call LM Studio with timeout."""
        try:
            import urllib.request
            
            payload = {
                "model": "local-model",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            req = urllib.request.Request(
                f"{self.lm_studio_url}/chat/completions",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            start_time = time.time()
            with urllib.request.urlopen(req, timeout=timeout) as response:
                elapsed = time.time() - start_time
                data = json.loads(response.read())
                result = data["choices"][0]["message"]["content"]
                
                # Log success
                self._log("local", len(prompt), elapsed)
                return result
                
        except Exception as e:
            self._log("local", len(prompt), 0, error=str(e))
            return None
    
    def route(self, prompt: str, context: str = "", force_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Smart route task to appropriate model.
        
        Returns dict with:
        - result: str
        - model_used: str
        - cost: float
        - time_elapsed: float
        """
        start_time = time.time()
        
        # Check for force model override
        if force_model and force_model in self.models:
            analysis = {"recommended_model": force_model, "estimated_tokens": len(prompt) // 4}
        else:
            analysis = self.analyze_task(prompt, context)
        
        recommended = analysis["recommended_model"]
        
        # Try local first if recommended
        if recommended == "local" and self.check_local_available():
            result = self.call_local(prompt)
            if result:
                elapsed = time.time() - start_time
                self.savings["local"] += 1
                self.savings["saved"] += 0.004  # Approx savings vs Kimi
                return {
                    "result": result,
                    "model_used": "local",
                    "cost": 0.0,
                    "time_elapsed": elapsed,
                    "analysis": analysis
                }
        
        # If local failed or not recommended, escalate
        if recommended == "local":
            recommended = "kimi"  # Fallback
        
        # For now, return escalation notice (actual Kimi/Opus calls would go here)
        elapsed = time.time() - start_time
        return {
            "result": None,
            "model_used": recommended,
            "cost": self.models[recommended]["cost_per_1k"] * (analysis["estimated_tokens"] / 1000),
            "time_elapsed": elapsed,
            "analysis": analysis,
            "escalation_reason": "Local unavailable or task too complex" if recommended != "local" else None
        }
    
    def _log(self, model: str, token_count: int, elapsed: float, error: Optional[str] = None):
        """Log routing decision."""
        with open(COST_LOG, "a") as f:
            timestamp = datetime.now().isoformat()
            if error:
                f.write(f"[{timestamp}] {model} FAILED: {error}\n")
            else:
                f.write(f"[{timestamp}] {model}: {token_count} tokens, {elapsed:.2f}s\n")
    
    def get_savings_report(self) -> str:
        """Get cost savings summary."""
        return f"""
💰 Cost Savings Report
━━━━━━━━━━━━━━━━━━━━━━━━
Local (FREE) tasks: {self.savings['local']}
Kimi tasks: {self.savings['kimi']}
Opus tasks: {self.savings['opus']}
Total saved vs all-Kimi: ${self.savings['saved']:.4f}
"""


# Convenience functions for direct use
def smart_complete(prompt: str, context: str = "", force_model: Optional[str] = None) -> str:
    """Complete a prompt using smart routing."""
    router = SmartRouter()
    result = router.route(prompt, context, force_model)
    
    if result["result"]:
        return result["result"]
    else:
        return f"[Escalated to {result['model_used']}] Task too complex for local model."


def test_local():
    """Test LM Studio connection."""
    router = SmartRouter()
    if router.check_local_available():
        print("✅ LM Studio is online")
        result = router.call_local("Say 'Local model working' if you can hear me.", max_tokens=20)
        if result:
            print(f"✅ Response: {result}")
        else:
            print("❌ Local model call failed")
    else:
        print("❌ LM Studio not available on :1234")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_local()
    else:
        # Demo
        router = SmartRouter()
        
        test_prompts = [
            "Summarize this file in 2 sentences",  # Should route local
            "Design a secure authentication system",  # Should escalate
            "What is 2+2?",  # Should route local
            "Analyze trading strategy risk factors",  # Should escalate
        ]
        
        for prompt in test_prompts:
            print(f"\n📝 Prompt: {prompt[:50]}...")
            analysis = router.analyze_task(prompt)
            print(f"   Analysis: {analysis['complexity']} complexity, ~{analysis['estimated_tokens']} tokens")
            print(f"   Recommended: {analysis['recommended_model']}")
