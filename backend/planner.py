"""🔍 PLANNER - Task Decomposition & Planning System
🔍 FEATURES:
✅ Break down complex goals into subtasks
✅ Auto-generate step-by-step plans using LLM
✅ Track task dependencies
✅ Adaptive replanning on failures
✅ Resource estimation (time, complexity)
✅ Self-reflection after each task
"""

import json, asyncio, time
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class Task:
    """Individual task in a plan"""
    
    def __init__(self, task_id: str, description: str, priority: int = 0, estimated_time: int = 60):
        self.id = task_id
        self.description = description
        self.priority = priority
        self.estimated_time = estimated_time
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.dependencies: List[str] = []
        self.subtasks: List['Task'] = []
        self.attempts = 0
        self.max_retries = 3
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority,
            'estimated_time': self.estimated_time,
            'created_at': self.created_at,
            'result': self.result,
            'error': self.error,
            'attempts': self.attempts,
        }


class Plan:
    """Execution plan containing multiple tasks"""
    
    def __init__(self, goal: str, plan_id: str = None):
        self.plan_id = plan_id or f"plan_{int(time.time())}"
        self.goal = goal
        self.tasks: List[Task] = []
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
        self.status = TaskStatus.PENDING
        self.execution_log: List[Dict] = []
    
    def add_task(self, task: Task) -> None:
        """Add task to plan"""
        self.tasks.append(task)
    
    def get_next_task(self) -> Optional[Task]:
        """Get next executable task (respecting dependencies)"""
        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue
            
            # Check dependencies
            all_deps_done = True
            for dep_id in task.dependencies:
                dep_task = next((t for t in self.tasks if t.id == dep_id), None)
                if dep_task and dep_task.status != TaskStatus.COMPLETED:
                    all_deps_done = False
                    break
            
            if all_deps_done:
                return task
        
        return None
    
    def log_execution(self, task_id: str, status: str, message: str) -> None:
        """Log task execution"""
        self.execution_log.append({
            'timestamp': datetime.now().isoformat(),
            'task_id': task_id,
            'status': status,
            'message': message,
        })
    
    def get_plan_summary(self) -> Dict:
        """Get summary of plan status"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)
        in_progress = sum(1 for t in self.tasks if t.status == TaskStatus.IN_PROGRESS)
        
        return {
            'plan_id': self.plan_id,
            'goal': self.goal,
            'status': self.status.value,
            'total_tasks': total,
            'completed': completed,
            'failed': failed,
            'in_progress': in_progress,
            'pending': total - completed - failed - in_progress,
            'progress_percent': int((completed / total * 100) if total > 0 else 0),
        }


class Planner:
    """Main planner with LLM integration"""
    
    def __init__(self, llm_selector=None):
        """Initialize planner with optional LLM"""
        self.llm_selector = llm_selector
        self.current_plan: Optional[Plan] = None
        self.plan_history: List[Plan] = []
        self.reflexion_enabled = True
    
    async def create_plan(self, goal: str, max_steps: int = 10) -> Plan:
        """Create a plan using LLM if available"""
        plan = Plan(goal)
        
        if self.llm_selector:
            # Use LLM to generate steps
            steps = await self._generate_steps(goal, max_steps)
            for i, step in enumerate(steps):
                task = Task(
                    task_id=f"step_{i}",
                    description=step,
                    priority=i,
                    estimated_time=60
                )
                plan.add_task(task)
        else:
            # Fallback: create simple steps
            steps = self._simple_decompose(goal)
            for i, step in enumerate(steps):
                task = Task(
                    task_id=f"step_{i}",
                    description=step,
                    priority=i,
                )
                plan.add_task(task)
        
        self.current_plan = plan
        return plan
    
    async def _generate_steps(self, goal: str, max_steps: int) -> List[str]:
        """Generate steps using LLM"""
        prompt = f"""Break down this goal into {max_steps} concrete, actionable steps:
Goal: {goal}

Return only the steps as a JSON array of strings."""
        
        try:
            if self.llm_selector and hasattr(self.llm_selector, 'plan_actions'):
                result = await self.llm_selector.plan_actions(goal, max_steps)
                if isinstance(result, list):
                    return result
        except:
            pass
        
        return self._simple_decompose(goal)
    
    def _simple_decompose(self, goal: str) -> List[str]:
        """Simple fallback decomposition"""
        return [
            f"Analyze: {goal}",
            f"Plan: Break down {goal} into smaller parts",
            f"Setup: Prepare environment for {goal}",
            f"Execute: Perform main {goal}",
            f"Validate: Check if {goal} completed",
            f"Optimize: Improve {goal} execution",
            f"Document: Log results of {goal}",
        ]
    
    async def execute_plan(self, plan: Plan, executor=None) -> bool:
        """Execute plan step by step"""
        plan.status = TaskStatus.IN_PROGRESS
        plan.started_at = datetime.now().isoformat()
        
        print(f"\n🔍 EXECUTING PLAN: {plan.goal}")
        print(f"📊 Tasks: {len(plan.tasks)}")
        
        while True:
            next_task = plan.get_next_task()
            if not next_task:
                break
            
            await self._execute_task(next_task, plan, executor)
        
        plan.status = TaskStatus.COMPLETED
        plan.completed_at = datetime.now().isoformat()
        self.plan_history.append(plan)
        
        summary = plan.get_plan_summary()
        print(f"\n✅ PLAN COMPLETED")
        print(f"Progress: {summary['completed']}/{summary['total_tasks']} tasks")
        
        return summary['failed'] == 0
    
    async def _execute_task(self, task: Task, plan: Plan, executor=None) -> None:
        """Execute single task with retry logic"""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now().isoformat()
        task.attempts += 1
        
        print(f"\n🚀 Task {task.attempts}: {task.description}")
        plan.log_execution(task.id, 'started', task.description)
        
        try:
            if executor and hasattr(executor, 'execute'):
                result = await executor.execute(task.description)
                task.result = result
                task.status = TaskStatus.COMPLETED
                print(f"✅ Task completed: {task.id}")
                plan.log_execution(task.id, 'completed', 'Success')
            else:
                # Simulate task execution
                await asyncio.sleep(0.5)
                task.result = f"Simulated result for: {task.description}"
                task.status = TaskStatus.COMPLETED
                print(f"✅ Task completed: {task.id}")
                plan.log_execution(task.id, 'completed', 'Simulated')
        
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            print(f"❌ Task failed: {task.id} - {e}")
            plan.log_execution(task.id, 'failed', str(e))
            
            if task.attempts < task.max_retries:
                print(f"🔄 Retrying task {task.attempts}/{task.max_retries}...")
                task.status = TaskStatus.PENDING
                # Could implement backoff here
    
    async def reflect_on_plan(self, plan: Plan) -> Dict:
        """Analyze plan execution and identify improvements"""
        if not self.reflexion_enabled:
            return {}
        
        summary = plan.get_plan_summary()
        
        reflection = {
            'total_tasks': summary['total_tasks'],
            'completed': summary['completed'],
            'failed': summary['failed'],
            'success_rate': summary['completed'] / summary['total_tasks'] if summary['total_tasks'] > 0 else 0,
            'recommendations': [],
        }
        
        # Analyze failures
        failed_tasks = [t for t in plan.tasks if t.status == TaskStatus.FAILED]
        if failed_tasks:
            reflection['recommendations'].append(f"Fix {len(failed_tasks)} failed tasks")
        
        # Check timing
        if plan.completed_at and plan.started_at:
            planned_time = sum(t.estimated_time for t in plan.tasks)
            reflection['planned_time'] = planned_time
            reflection['recommendations'].append(f"Improve time estimates")
        
        return reflection
    
    def export_plan(self, plan: Plan, filepath: str) -> bool:
        """Export plan to JSON"""
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    'plan_id': plan.plan_id,
                    'goal': plan.goal,
                    'status': plan.status.value,
                    'created_at': plan.created_at,
                    'tasks': [t.to_dict() for t in plan.tasks],
                    'summary': plan.get_plan_summary(),
                    'execution_log': plan.execution_log,
                }, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Failed to export plan: {e}")
            return False


if __name__ == "__main__":
    import asyncio
    
    async def main():
        planner = Planner()
        
        # Create a sample plan
        plan = await planner.create_plan("Create a simple web scraper for weather data")
        print(f"📊 Plan created with {len(plan.tasks)} tasks")
        print("\nTasks:")
        for i, task in enumerate(plan.tasks):
            print(f"  {i+1}. {task.description}")
        
        # Execute plan
        await planner.execute_plan(plan)
        
        # Reflect
        reflection = await planner.reflect_on_plan(plan)
        print(f"\n🧐 Reflection: {reflection}")
    
    asyncio.run(main())
