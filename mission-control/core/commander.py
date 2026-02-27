"""
NEMO Mission Control - Commander Module
Orchestrates multi-agent task delegation and coordination
"""
import json
import uuid
import re
from datetime import datetime
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

@dataclass
class Task:
    """A task to be delegated to a sub-agent."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    agent_id: str = ""
    description: str = ""
    prompt: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    session_key: Optional[str] = None
    parent_task: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    cost: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "status": self.status.value,
            "priority": self.priority.value
        }

class Commander:
    """
    Central orchestrator for Multi-Agent Mission Control.
    
    Usage:
        commander = Commander()
        task = commander.delegate("researcher", "Analyze Polymarket fees")
        result = commander.wait_for(task.id)
    """
    
    def __init__(self, config_path: str = "mission-control/config/agents.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.tasks: Dict[str, Task] = {}
        self.active_sessions: Dict[str, str] = {}  # task_id -> session_key
        
    def _load_config(self) -> dict:
        """Load agent configuration."""
        try:
            with open(self.config_path) as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load config: {e}")
            return {"agents": {}, "defaults": {}, "routing": {"taskPatterns": []}}
    
    def get_agent_config(self, agent_id: str) -> Optional[dict]:
        """Get configuration for a specific agent."""
        return self.config.get("agents", {}).get(agent_id)
    
    def list_agents(self) -> List[dict]:
        """List all available agents."""
        return [
            {"id": k, **v} 
            for k, v in self.config.get("agents", {}).items()
            if v.get("enabled", True)
        ]
    
    def route_task(self, description: str) -> Optional[str]:
        """
        Automatically route a task to the appropriate agent based on keywords.
        
        Args:
            description: Task description to analyze
            
        Returns:
            Agent ID or None if no match
        """
        description_lower = description.lower()
        patterns = self.config.get("routing", {}).get("taskPatterns", [])
        
        for pattern in patterns:
            regex = pattern.get("pattern", "")
            agent = pattern.get("agent", "")
            if re.search(regex, description_lower):
                return agent
        
        return None
    
    def delegate(
        self, 
        agent_id: str, 
        description: str, 
        prompt: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        parent_task: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Task:
        """
        Delegate a task to a sub-agent.
        
        Args:
            agent_id: Which agent to use (researcher, coder, trader, etc.)
            description: Short task description
            prompt: Full prompt for the agent (defaults to description)
            priority: Task priority level
            parent_task: Parent task ID if this is a subtask
            timeout: Override default timeout
            
        Returns:
            Task object with ID and status
        """
        agent_config = self.get_agent_config(agent_id)
        if not agent_config:
            raise ValueError(f"Unknown agent: {agent_id}")
        
        if not agent_config.get("enabled", True):
            raise ValueError(f"Agent {agent_id} is disabled")
        
        task = Task(
            agent_id=agent_id,
            description=description,
            prompt=prompt or description,
            priority=priority,
            parent_task=parent_task
        )
        
        self.tasks[task.id] = task
        
        # Get agent settings
        model = agent_config.get("model", "kimi-k2.5")
        task_timeout = timeout or agent_config.get("timeoutSeconds", 300)
        
        print(f"🚀 Delegating to {agent_id}: {description}")
        print(f"   Task ID: {task.id}")
        print(f"   Priority: {priority.name}")
        print(f"   Timeout: {task_timeout}s")
        print(f"   Model: {model}")
        
        # In a real implementation, this would call sessions_spawn
        # For now, we log the delegation and return the task
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        
        return task
    
    def delegate_auto(
        self, 
        description: str, 
        prompt: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM
    ) -> Task:
        """
        Automatically route and delegate a task.
        
        Args:
            description: Task description (used for routing)
            prompt: Full prompt (optional)
            priority: Task priority
            
        Returns:
            Task object
        """
        agent_id = self.route_task(description)
        if not agent_id:
            raise ValueError(f"Could not route task: {description}")
        
        return self.delegate(agent_id, description, prompt, priority)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def get_status(self) -> dict:
        """Get overall system status."""
        status_counts = {s: 0 for s in TaskStatus}
        for task in self.tasks.values():
            status_counts[task.status] += 1
        
        return {
            "total_tasks": len(self.tasks),
            "active_tasks": sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING),
            "completed_tasks": sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
            "failed_tasks": sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED),
            "status_breakdown": {k.value: v for k, v in status_counts.items()},
            "agents_available": len(self.list_agents())
        }
    
    def list_active_tasks(self) -> List[Task]:
        """List all currently running tasks."""
        return [t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.CANCELLED
            print(f"🛑 Cancelled task {task_id}")
            return True
        
        return False
    
    def parallel_delegate(
        self, 
        tasks: List[tuple],
        wait_for_all: bool = False
    ) -> List[Task]:
        """
        Delegate multiple tasks in parallel.
        
        Args:
            tasks: List of (agent_id, description, prompt) tuples
            wait_for_all: Whether to block until all complete
            
        Returns:
            List of Task objects
        """
        delegated = []
        for task_spec in tasks:
            if len(task_spec) >= 2:
                agent_id = task_spec[0]
                description = task_spec[1]
                prompt = task_spec[2] if len(task_spec) > 2 else None
                priority = task_spec[3] if len(task_spec) > 3 else TaskPriority.MEDIUM
                
                task = self.delegate(agent_id, description, prompt, priority)
                delegated.append(task)
        
        print(f"\n📊 Delegated {len(delegated)} tasks in parallel")
        return delegated
    
    def generate_report(self) -> str:
        """Generate a summary report of all activity."""
        status = self.get_status()
        
        report = []
        report.append("=" * 60)
        report.append("🎯 MISSION CONTROL REPORT")
        report.append("=" * 60)
        report.append(f"Total Tasks: {status['total_tasks']}")
        report.append(f"Active: {status['active_tasks']} | Completed: {status['completed_tasks']} | Failed: {status['failed_tasks']}")
        report.append(f"Agents Available: {status['agents_available']}")
        report.append("")
        
        if self.list_active_tasks():
            report.append("🔥 Active Tasks:")
            for task in self.list_active_tasks():
                report.append(f"   [{task.id}] {task.agent_id}: {task.description}")
        
        recent_completed = [
            t for t in self.tasks.values() 
            if t.status == TaskStatus.COMPLETED
        ][-5:]
        
        if recent_completed:
            report.append("")
            report.append("✅ Recently Completed:")
            for task in recent_completed:
                report.append(f"   [{task.id}] {task.description}")
        
        report.append("=" * 60)
        return "\n".join(report)


# Convenience functions for direct use
def quick_delegate(agent_id: str, description: str, prompt: Optional[str] = None) -> Task:
    """Quickly delegate a single task."""
    cmdr = Commander()
    return cmdr.delegate(agent_id, description, prompt)

def quick_parallel(tasks: List[tuple]) -> List[Task]:
    """Quickly delegate multiple tasks in parallel."""
    cmdr = Commander()
    return cmdr.parallel_delegate(tasks)


def demo():
    """Demonstration of Commander capabilities."""
    print("🐟 NEMO Mission Control - Commander Demo\n")
    
    cmdr = Commander()
    
    # Show available agents
    print("📋 Available Agents:")
    for agent in cmdr.list_agents():
        print(f"   • {agent['id']}: {agent['description']} ({agent['model']})")
    print()
    
    # Demonstrate routing
    test_tasks = [
        "Research Polymarket trading strategies",
        "Fix bug in trading bot",
        "Execute snipe trade on BTC market",
        "Audit security of new code",
        "Generate daily P&L report"
    ]
    
    print("🎯 Task Routing Examples:")
    for task in test_tasks:
        routed = cmdr.route_task(task)
        print(f"   '{task}' → {routed or 'NO MATCH'}")
    print()
    
    # Demonstrate delegation
    print("🚀 Simulating Task Delegation:")
    
    # Parallel delegation example
    parallel_tasks = [
        ("researcher", "Research Polymarket fees", "Find current fee structure"),
        ("analyst", "Analyze win rates", "Calculate expected value"),
        ("coder", "Update strategy", "Implement fee handling")
    ]
    
    tasks = cmdr.parallel_delegate(parallel_tasks)
    print()
    
    # Show status
    print(cmdr.generate_report())
    
    print("\n✨ Demo complete!")


if __name__ == "__main__":
    demo()
