"""Performance dashboard component for monitoring application health."""

import streamlit as st
import json
import time
from typing import Dict, Any
from utils.performance_monitor import get_performance_monitor
from utils.cache_manager import get_cache_manager
from utils.logger import get_application_metrics


class PerformanceDashboard:
    """Performance monitoring dashboard component."""
    
    def __init__(self):
        """Initialize performance dashboard."""
        self.monitor = get_performance_monitor()
        self.cache_manager = get_cache_manager()
        self.metrics = get_application_metrics()
    
    def render_sidebar_metrics(self):
        """Render performance metrics in sidebar."""
        with st.sidebar:
            with st.expander("📊 Performance Metrics", expanded=False):
                self._render_quick_stats()
    
    def render_full_dashboard(self):
        """Render full performance dashboard."""
        st.header("📊 Performance & Monitoring Dashboard")
        
        # Performance summary
        col1, col2, col3, col4 = st.columns(4)
        
        summary = self.monitor.get_performance_summary()
        cache_stats = self.cache_manager.get_stats()
        app_metrics = self.metrics.get_summary()
        
        with col1:
            st.metric(
                "Uptime",
                f"{summary['uptime_seconds'] / 3600:.1f}h",
                help="Application uptime in hours"
            )
            
        with col2:
            st.metric(
                "Requests",
                f"{summary['application']['total_requests']}",
                help="Total requests processed"
            )
            
        with col3:
            st.metric(
                "Error Rate",
                f"{summary['application']['error_rate_percent']:.1f}%",
                delta=f"-{summary['application']['error_rate_percent']:.1f}%" if summary['application']['error_rate_percent'] < 5 else None,
                help="Current error rate percentage"
            )
            
        with col4:
            st.metric(
                "Cache Hit Rate",
                f"{cache_stats['hit_rate']:.1f}%",
                delta=f"+{cache_stats['hit_rate']:.1f}%" if cache_stats['hit_rate'] > 70 else None,
                help="Cache efficiency percentage"
            )
        
        # System metrics
        st.subheader("🖥️ System Metrics")
        
        sys_col1, sys_col2, sys_col3 = st.columns(3)
        
        with sys_col1:
            st.write("**Memory Usage**")
            memory_mb = summary['system']['memory']['process_memory_mb']
            st.metric("Process Memory", f"{memory_mb:.1f} MB")
            st.metric("System Memory", f"{summary['system']['memory']['system_memory_percent']:.1f}%")
            
        with sys_col2:
            st.write("**CPU Usage**")
            st.metric("Process CPU", f"{summary['system']['cpu']['process_cpu_percent']:.1f}%")
            st.metric("System CPU", f"{summary['system']['cpu']['system_cpu_percent']:.1f}%")
            
        with sys_col3:
            st.write("**Disk Usage**")
            st.metric("Disk Usage", f"{summary['system']['disk']['disk_usage_percent']:.1f}%")
            st.metric("Free Space", f"{summary['system']['disk']['disk_free_gb']:.1f} GB")
        
        # Cache details
        st.subheader("🗄️ Cache Performance")
        
        cache_col1, cache_col2 = st.columns(2)
        
        with cache_col1:
            st.write("**Cache Statistics**")
            st.json({
                "Total Requests": cache_stats['total_requests'],
                "Cache Hits": cache_stats['hits'],
                "Cache Misses": cache_stats['misses'],
                "Hit Rate": f"{cache_stats['hit_rate']:.2f}%",
                "Memory Cache Size": cache_stats['memory_size']
            })
            
        with cache_col2:
            st.write("**Cache Distribution**")
            if cache_stats['total_requests'] > 0:
                st.bar_chart({
                    'Memory Hits': cache_stats['memory_hits'],
                    'Disk Hits': cache_stats['disk_hits'],
                    'Redis Hits': cache_stats['redis_hits'],
                    'Misses': cache_stats['misses']
                })
        
        # Application metrics
        st.subheader("📱 Application Metrics")
        
        app_col1, app_col2 = st.columns(2)
        
        with app_col1:
            st.write("**Processing Statistics**")
            st.json({
                "Files Processed": app_metrics['files_processed'],
                "Average Processing Time": f"{app_metrics['avg_processing_time']:.2f}s",
                "Average File Size": f"{app_metrics['avg_file_size']:.1f} bytes",
                "Security Events": app_metrics['security_events']
            })
            
        with app_col2:
            st.write("**Operation Performance**")
            if summary['operations']:
                operations_data = {}
                for op, data in summary['operations'].items():
                    operations_data[op] = data['avg_time']
                st.bar_chart(operations_data)
        
        # Recent activity
        st.subheader("📈 Recent Activity (5 minutes)")
        
        recent_requests = summary['application']['recent_requests']
        recent_errors = summary['application']['recent_errors']
        
        if recent_requests:
            st.write("**Request Activity**")
            st.json(recent_requests)
        
        if recent_errors:
            st.write("**Error Activity**")
            st.json(recent_errors)
        
        # Health status
        st.subheader("🔋 Health Status")
        
        health_status = self._calculate_health_status(summary, cache_stats)
        
        if health_status['status'] == 'healthy':
            st.success(f"✅ System Status: {health_status['status'].upper()}")
        elif health_status['status'] == 'warning':
            st.warning(f"⚠️ System Status: {health_status['status'].upper()}")
        else:
            st.error(f"❌ System Status: {health_status['status'].upper()}")
        
        for issue in health_status['issues']:
            st.write(f"• {issue}")
        
        # Raw metrics export
        with st.expander("🔧 Raw Metrics (JSON)", expanded=False):
            full_data = {
                'performance_summary': summary,
                'cache_stats': cache_stats,
                'application_metrics': app_metrics,
                'timestamp': time.time()
            }
            st.json(full_data)
            
            st.download_button(
                "📥 Download Metrics",
                data=json.dumps(full_data, indent=2),
                file_name=f"performance_metrics_{int(time.time())}.json",
                mime="application/json"
            )
    
    def _render_quick_stats(self):
        """Render quick performance stats."""
        try:
            summary = self.monitor.get_performance_summary()
            cache_stats = self.cache_manager.get_stats()
            
            # Quick metrics
            st.metric("Memory", f"{summary['system']['memory']['process_memory_mb']:.1f}MB")
            st.metric("CPU", f"{summary['system']['cpu']['process_cpu_percent']:.1f}%")
            st.metric("Cache Hit Rate", f"{cache_stats['hit_rate']:.1f}%")
            st.metric("Error Rate", f"{summary['application']['error_rate_percent']:.1f}%")
            
            # Health indicator
            health = self._calculate_health_status(summary, cache_stats)
            
            if health['status'] == 'healthy':
                st.success("System Healthy ✅")
            elif health['status'] == 'warning':
                st.warning("System Warning ⚠️")
            else:
                st.error("System Issues ❌")
                
        except Exception as e:
            st.error(f"Metrics unavailable: {str(e)}")
    
    def _calculate_health_status(self, summary: Dict[str, Any], cache_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall system health status."""
        issues = []
        status = 'healthy'
        
        # Check memory usage
        memory_percent = summary['system']['memory']['process_memory_mb']
        if memory_percent > 1000:  # > 1GB
            issues.append("High memory usage detected")
            status = 'warning'
        
        # Check error rate
        error_rate = summary['application']['error_rate_percent']
        if error_rate > 10:
            issues.append(f"High error rate: {error_rate:.1f}%")
            status = 'critical'
        elif error_rate > 5:
            issues.append(f"Elevated error rate: {error_rate:.1f}%")
            status = 'warning'
        
        # Check cache performance
        cache_hit_rate = cache_stats['hit_rate']
        if cache_hit_rate < 50:
            issues.append(f"Low cache hit rate: {cache_hit_rate:.1f}%")
            status = 'warning'
        
        # Check CPU usage
        cpu_percent = summary['system']['cpu']['process_cpu_percent']
        if cpu_percent > 80:
            issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            status = 'warning'
        
        if not issues:
            issues.append("All systems operating normally")
        
        return {
            'status': status,
            'issues': issues
        }