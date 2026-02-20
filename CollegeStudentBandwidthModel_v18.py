# v18 14:23 16FEB2026
#
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import csv
from pathlib import Path

class CollegeStudentBandwidthModel:
    """
    v15 - DataFrame Edition
    Models 24-hour bandwidth consumption with CSV import/export capabilities.
    Supports device parameters, usage patterns, and scenario management.
    """
    
    def __init__(self, config_file=None):
        self.hours = np.arange(0, 24, 0.5)  # 30-minute intervals (48 points)
        
        # Device configuration with detailed parameters
        self.device_config = pd.DataFrame({
            'device': ['laptop', 'smartphone', 'tablet', 'smartwatch'],
            'display_name': ['Laptop', 'Smartphone', 'Tablet', 'Smartwatch'],
            'color': ['#4ECDC4', '#FF6B6B', '#45B7D1', '#FFA07A'],
            'line_style': ['-', '-', '-', '--'],
            'wifi_capability': ['WiFi 6E', 'WiFi 6E', 'WiFi 6', 'WiFi 4'],
            'max_bandwidth_mbps': [100, 50, 40, 5],
            'typical_usage_mbps': [15, 8, 5, 0.2],
            'power_mode': ['high', 'medium', 'medium', 'low'],
            'preferred_band': ['6GHz', '5GHz', '5GHz', '2.4GHz'],
            'device_count': [1, 1, 1, 1],
            'enabled': [True, True, True, True]
        })
        
        # Usage pattern parameters
        self.usage_params = pd.DataFrame({
            'time_slot': ['00:00-06:00', '06:00-09:00', '09:00-12:00', 
                         '12:00-15:00', '15:00-18:00', '18:00-22:00', '22:00-24:00'],
            'period_name': ['Sleep', 'Morning Routine', 'Classes', 
                           'Lunch/Study', 'Afternoon Activities', 'Evening Prime Time', 'Wind Down'],
            'laptop_multiplier': [0.1, 0.8, 0.9, 1.2, 0.6, 1.5, 1.3],
            'smartphone_multiplier': [0.2, 1.0, 0.8, 1.5, 0.6, 1.2, 1.0],
            'tablet_multiplier': [0.5, 0.6, 0.8, 1.0, 0.5, 1.5, 1.2],
            'smartwatch_multiplier': [0.1, 1.5, 0.8, 0.6, 2.0, 0.8, 0.5],
            'concurrent_usage_factor': [0.3, 0.7, 0.6, 0.8, 0.5, 1.0, 0.8]
        })
        
        # Application/Activity bandwidth requirements
        self.app_bandwidth = pd.DataFrame({
            'application': ['4K Streaming', '1080p Streaming', '720p Streaming',
                          'Video Call HD', 'Video Call SD', 'Online Gaming',
                          'Web Browsing', 'Social Media', 'Music Streaming',
                          'Cloud Sync', 'Email', 'Messaging', 'Background Idle'],
            'bandwidth_mbps': [25, 8, 3, 4, 1.5, 3, 2, 5, 1.5, 5, 0.5, 0.3, 0.1],
            'latency_sensitive': [False, False, False, True, True, True, 
                                False, False, False, False, False, False, False],
            'preferred_band': ['6GHz', '5GHz', '5GHz', '6GHz', '5GHz', '6GHz',
                             '5GHz', '5GHz', '5GHz', '5GHz', '2.4GHz', '2.4GHz', '2.4GHz']
        })
        
        # QoS Priority levels
        self.qos_priority = pd.DataFrame({
            'priority_level': [1, 2, 3, 4, 5],
            'category': ['Critical', 'High', 'Medium', 'Low', 'Background'],
            'description': ['Video calls, Gaming', 'Streaming video', 
                          'Web browsing, Social media', 'Downloads, Updates',
                          'Background sync, Idle'],
            'bandwidth_guarantee_percent': [40, 30, 20, 10, 5]
        })
        
        # Environmental factors
        self.environment_factors = pd.DataFrame({
            'factor': ['Dorm WiFi Congestion', 'Number of Nearby Networks', 
                      'Time of Day Traffic', 'Building Material Interference',
                      'Distance from Router'],
            'impact_level': ['High', 'Medium', 'High', 'Low', 'Medium'],
            'bandwidth_penalty_percent': [15, 8, 20, 5, 10],
            'affects_band': ['5GHz/6GHz', 'All', 'All', '5GHz', '2.4GHz']
        })
        
        # Load config if provided
        if config_file:
            self.load_config(config_file)
        
        # Generate initial data
        self.bandwidth_data = self._generate_bandwidth_data()
        self.wifi_band_data = self._generate_wifi_band_data()
        self.activities = self._generate_activity_descriptions()
        
        # Create time-series DataFrame for detailed analysis
        self.timeseries_df = self._create_timeseries_dataframe()
    
    def _generate_bandwidth_data(self):
        """Generate bandwidth consumption data based on device config and usage patterns"""
        data = {}
        
        # Base patterns (can be overridden by CSV import)
        base_patterns = {
            'smartphone': np.array([1,0.5,0.3,0.2,0.2,0.3,2,3,5,4,8,12,10,8,5,3,2,1.5,1,1.5,2,5,10,8,12,15,8,4,3,2,3,2.5,2,1.5,3,4,5,8,10,12,8,6,10,12,8,10,8,6]),
            'laptop': np.array([20,15,0.5,0.3,0.3,0.5,1,0.8,1,2,3,5,8,12,15,8,5,4,6,10,8,12,10,6,12,10,8,15,18,12,8,10,12,8,5,3,15,20,25,22,18,12,8,10,15,20,22,20]),
            'tablet': np.array([1,2,1.5,1,0.5,0.5,0.3,0.2,0.2,0.3,1,2,3,2,1,0.5,0.3,2,3,2.5,2,3,2,1.5,2,3,4,3,2.5,2,1.5,1,0.5,0.3,2,4,3,5,8,10,6,4,2,3,8,12,10,8]),
            'smartwatch': np.array([0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.02,0.05,0.08,0.1,0.15,0.12,0.5,0.3,0.1,0.08,0.1,0.15,0.1,0.08,0.06,0.05,0.08,0.1,0.08,0.06,0.05,0.1,0.25,0.3,0.2,0.15,0.1,0.08,0.1,0.12,0.15,0.1,0.08,0.06,0.05,0.08,0.1,0.06,0.04,0.02])
        }
        
        for _, device in self.device_config.iterrows():
            if device['enabled']:
                device_name = device['device']
                base_pattern = base_patterns.get(device_name, np.ones(48) * device['typical_usage_mbps'])
                
                # Scale by device count
                scaled_pattern = base_pattern * device['device_count']
                
                # Clip to max bandwidth
                data[device_name] = np.clip(scaled_pattern, 0, device['max_bandwidth_mbps'])
            else:
                data[device_name] = np.zeros(48)
        
        return data
    
    def _generate_wifi_band_data(self):
        """Generate WiFi band usage based on device preferences and bandwidth needs"""
        band_data = {
            '2.4GHz': np.zeros(48),
            '5GHz': np.zeros(48),
            '6GHz': np.zeros(48)
        }
        
        for i in range(48):
            for _, device in self.device_config.iterrows():
                if not device['enabled']:
                    continue
                    
                device_name = device['device']
                bw = self.bandwidth_data[device_name][i]
                preferred = device['preferred_band']
                
                # Allocate bandwidth to preferred band with fallback logic
                if preferred == '6GHz' and device['wifi_capability'] == 'WiFi 6E':
                    if bw > 15:  # High bandwidth -> 6GHz
                        band_data['6GHz'][i] += bw
                    elif bw > 5:
                        band_data['5GHz'][i] += bw
                    else:
                        band_data['2.4GHz'][i] += bw
                elif preferred == '5GHz' or preferred == '6GHz':
                    if bw > 3:
                        band_data['5GHz'][i] += bw
                    else:
                        band_data['2.4GHz'][i] += bw
                else:  # 2.4GHz preferred
                    band_data['2.4GHz'][i] += bw
        
        return band_data
    
    def _generate_activity_descriptions(self):
        """Generate activity descriptions for each time slot"""
        activities = [
            "Streaming Netflix 4K in bed\nMessaging friends\nSleep prep",
            "Finishing movie, winding down\nLate night social media scroll",
            "Devices entering sleep mode\nCloud photo backup starting",
            "Deep sleep mode\nBackground system updates",
            "Sleep tracking active\nScheduled cloud backup",
            "Minimal network activity\nPeriodic sync checks",
            "Deep sleep continues\niCloud/Google backup window",
            "Background maintenance\nApp updates downloading",
            "Continued backup sync\nOS updates",
            "Low activity period\nBackup completion",
            "Pre-wake prep\nCalendar/email pre-sync",
            "System wake routines\nWeather/news cache update",
            "ALARM! First phone check\nEmail sync, Instagram, news",
            "Getting ready routine\nSpotify streaming\nHealth sync",
            "Breakfast time\nPodcast listening\nBackground refresh",
            "Pre-class prep\nDownloading slides\nLMS access",
            "Reviewing notes\nPDF textbook download\nSchedule check",
            "Walking to class\nCampus WiFi\nMusic continues",
            "First lecture starts\nCloud note-taking\nDigital textbook",
            "Lecture continues\nReference lookup\nRecording stream",
            "Class wrapping up\nSaving notes\nQuick email",
            "BREAK - Coffee & social media\nTikTok, Snapchat\nShort-form video",
            "Second class - Discussion\nCollaborative docs\nScreen share",
            "Active participation\nReal-time research\nFact-checking",
            "Lunch at dining hall\nYouTube videos\nSocial catch-up",
            "Lunch continues\nGroup chat\nPlanning afternoon",
            "Library study begins\nDatabase research\nJSTOR, PubMed",
            "Deep research mode\nPDF downloads\nReference manager",
            "Writing research paper\nGoogle Docs\nSpotify music",
            "Continued writing\nMultiple tabs\nCitation management",
            "Gym time!\nFitness tracking\nWorkout app sync",
            "Workout continues\nMusic streaming\nQuick social checks",
            "Post-gym, heading back\nWiFi transition\nMusic continues",
            "Quick shower\nReconnecting to dorm WiFi\nDay's data syncing",
            "Homework starts\nVideo tutorials\nCoding environment",
            "Intensive project work\nMultiple tabs\nCloud storage sync",
            "Homework continues\nGitHub activity\nMulti-device productivity",
            "Dinner time!\nNetflix/YouTube\nTexting friends",
            "Dinner entertainment\nStreaming content\nSocial browsing",
            "Study group video call\nZoom/Discord 1080p\nScreen sharing",
            "Video call continues\nNote-taking\nShared presentations",
            "Call wrapping up\nFinalizing notes\nScheduling next",
            "Social/Gaming hour\nOnline gaming\nDiscord voice",
            "Continued gaming/social\nHeavy social media\nMobile games",
            "Evening wind-down\n4K streaming\nMessaging friends",
            "Binge watching\nTwitch stream\nLast social checks",
            "Pre-sleep routine\nTikTok/Instagram scroll\nMeditation app",
            "Getting ready for bed\nSetting alarms\nDevices to sleep mode"
        ]
        return activities
    
    def _create_timeseries_dataframe(self):
        """Create detailed time-series DataFrame for analysis"""
        time_labels = [f"{int(h):02d}:{int((h % 1) * 60):02d}" for h in self.hours]
        
        df = pd.DataFrame({
            'time': time_labels,
            'hour_decimal': self.hours,
        })
        
        # Add device bandwidth columns
        for device in ['laptop', 'smartphone', 'tablet', 'smartwatch']:
            df[f'{device}_mbps'] = self.bandwidth_data.get(device, np.zeros(48))
        
        # Add WiFi band columns
        for band in ['2.4GHz', '5GHz', '6GHz']:
            df[f'band_{band}'] = self.wifi_band_data[band]
        
        # Calculate totals and metrics
        df['total_mbps'] = df[[f'{d}_mbps' for d in ['laptop', 'smartphone', 'tablet', 'smartwatch']]].sum(axis=1)
        df['total_band_mbps'] = df[['band_2.4GHz', 'band_5GHz', 'band_6GHz']].sum(axis=1)
        
        # Add time-of-day categories
        df['period'] = pd.cut(df['hour_decimal'], 
                             bins=[0, 6, 9, 12, 15, 18, 22, 24],
                             labels=['Sleep', 'Morning', 'Classes', 'Midday', 'Afternoon', 'Evening', 'Night'])
        
        # Add activity descriptions
        df['activity'] = self.activities
        
        return df
    
    def export_device_config(self, filename='device_config.csv'):
        """Export device configuration to CSV"""
        self.device_config.to_csv(filename, index=False)
        print(f"✅ Device config exported to: {filename}")
    
    def import_device_config(self, filename='device_config.csv'):
        """Import device configuration from CSV"""
        self.device_config = pd.read_csv(filename)
        print(f"✅ Device config imported from: {filename}")
        # Regenerate data with new config
        self.bandwidth_data = self._generate_bandwidth_data()
        self.wifi_band_data = self._generate_wifi_band_data()
        self.timeseries_df = self._create_timeseries_dataframe()
    
    def export_usage_params(self, filename='usage_params.csv'):
        """Export usage pattern parameters to CSV"""
        self.usage_params.to_csv(filename, index=False)
        print(f"✅ Usage parameters exported to: {filename}")
    
    def import_usage_params(self, filename='usage_params.csv'):
        """Import usage pattern parameters from CSV"""
        self.usage_params = pd.read_csv(filename)
        print(f"✅ Usage parameters imported from: {filename}")
    
    def export_app_bandwidth(self, filename='app_bandwidth.csv'):
        """Export application bandwidth requirements to CSV"""
        self.app_bandwidth.to_csv(filename, index=False)
        print(f"✅ App bandwidth data exported to: {filename}")
    
    def import_app_bandwidth(self, filename='app_bandwidth.csv'):
        """Import application bandwidth requirements from CSV"""
        self.app_bandwidth = pd.read_csv(filename)
        print(f"✅ App bandwidth data imported from: {filename}")
    
    def export_timeseries(self, filename='timeseries_data.csv'):
        """Export full time-series data to CSV"""
        self.timeseries_df.to_csv(filename, index=False)
        print(f"✅ Time-series data exported to: {filename}")
    
    def export_all_data(self, prefix='bandwidth_model'):
        """Export all data tables to CSV files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.export_device_config(f'{prefix}_devices_{timestamp}.csv')
        self.export_usage_params(f'{prefix}_usage_{timestamp}.csv')
        self.export_app_bandwidth(f'{prefix}_apps_{timestamp}.csv')
        self.export_timeseries(f'{prefix}_timeseries_{timestamp}.csv')
        self.device_config.to_csv(f'{prefix}_devices_{timestamp}.csv', index=False)
        
        print(f"\n✅ All data exported with prefix: {prefix}_{timestamp}")
    
    def get_total_bandwidth(self):
        """Calculate total bandwidth across all devices"""
        total = np.zeros_like(self.hours)
        for device in self.bandwidth_data.values():
            total += device
        return total
    
    def get_statistics(self):
        """Calculate and return key statistics"""
        total = self.get_total_bandwidth()
        
        stats = {
            'peak_bandwidth': np.max(total),
            'peak_time': self.hours[np.argmax(total)],
            'average_bandwidth': np.mean(total),
            'total_daily_data_gb': np.sum(total) * 0.5 * 3600 / (8 * 1024),
            'device_contributions': {},
            'wifi_band_usage': {}
        }
        
        # Device stats
        for device, data in self.bandwidth_data.items():
            stats['device_contributions'][device] = {
                'average_mbps': np.mean(data),
                'peak_mbps': np.max(data),
                'percentage_of_total': (np.sum(data) / np.sum(total)) * 100
            }
        
        # WiFi band stats
        for band, data in self.wifi_band_data.items():
            stats['wifi_band_usage'][band] = {
                'average_mbps': np.mean(data),
                'peak_mbps': np.max(data),
                'percentage_of_total': (np.sum(data) / np.sum(total)) * 100
            }
        
        return stats
    
    def print_statistics(self):
        """Print formatted statistics"""
        stats = self.get_statistics()
        
        print("=" * 70)
        print("COLLEGE STUDENT BANDWIDTH ANALYSIS - v15")
        print("=" * 70)
        print(f"\n📊 Overall Statistics:")
        print(f"  Peak Bandwidth: {stats['peak_bandwidth']:.1f} Mbps at {int(stats['peak_time']):02d}:{int((stats['peak_time'] % 1) * 60):02d}")
        print(f"  Average Bandwidth: {stats['average_bandwidth']:.1f} Mbps")
        print(f"  Estimated Daily Data: {stats['total_daily_data_gb']:.1f} GB")
        
        print(f"\n📱 Device Breakdown:")
        for device, device_stats in stats['device_contributions'].items():
            device_info = self.device_config[self.device_config['device'] == device].iloc[0]
            print(f"\n  {device_info['display_name']} ({device_info['wifi_capability']}):")
            print(f"    Average: {device_stats['average_mbps']:.2f} Mbps")
            print(f"    Peak: {device_stats['peak_mbps']:.1f} Mbps")
            print(f"    % of Total: {device_stats['percentage_of_total']:.1f}%")
        
        print(f"\n📡 WiFi Band Utilization:")
        for band, band_stats in stats['wifi_band_usage'].items():
            print(f"\n  {band}:")
            print(f"    Average: {band_stats['average_mbps']:.2f} Mbps")
            print(f"    Peak: {band_stats['peak_mbps']:.1f} Mbps")
            print(f"    % of Total: {band_stats['percentage_of_total']:.1f}%")
        
        print("\n" + "=" * 70)
    
    def print_dataframe_summary(self):
        """Print summary of available DataFrames"""
        print("\n" + "=" * 70)
        print("AVAILABLE DATA TABLES")
        print("=" * 70)
        
        print("\n1. Device Configuration:")
        print(self.device_config.to_string(index=False))
        
        print("\n2. Usage Parameters (Time-based multipliers):")
        print(self.usage_params.to_string(index=False))
        
        print("\n3. Application Bandwidth Requirements:")
        print(self.app_bandwidth.to_string(index=False))
        
        print("\n4. QoS Priority Levels:")
        print(self.qos_priority.to_string(index=False))
        
        print("\n5. Environment Factors:")
        print(self.environment_factors.to_string(index=False))
        
        print("\n6. Time-series Data Sample (first 10 rows):")
        print(self.timeseries_df.head(10).to_string(index=False))
        
        print("\n" + "=" * 70)
    
    def plot_overlaid_devices(self, figsize=(16, 12)):
        """Create visualization with overlaid device lines and WiFi band breakdown"""
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(4, 2, height_ratios=[2.5, 2.5, 1.5, 1], hspace=0.35, wspace=0.3)
        
        # Main overlaid plot
        ax_overlay = fig.add_subplot(gs[0, :])
        
        self.device_lines = {}
        
        for _, device in self.device_config.iterrows():
            if not device['enabled']:
                continue
                
            device_name = device['device']
            data = self.bandwidth_data[device_name]
            
            linewidth = 3 if device['line_style'] == '--' else 2.5
            line, = ax_overlay.plot(self.hours, data, 
                                   color=device['color'],
                                   linewidth=linewidth, 
                                   alpha=0.9 if device['line_style'] == '--' else 0.8,
                                   label=device['display_name'],
                                   linestyle=device['line_style'])
            self.device_lines[device_name] = line
        
        ax_overlay.set_ylabel('Bandwidth (Mbps)', fontsize=12, fontweight='bold')
        ax_overlay.set_title('Device Bandwidth Overlay - All Devices in Mbps', 
                           fontsize=14, fontweight='bold')
        ax_overlay.legend(loc='upper left', framealpha=0.95, fontsize=11)
        ax_overlay.grid(True, alpha=0.3, linestyle='--')
        ax_overlay.set_xlim(0, 24)
        ax_overlay.set_xticks(range(0, 25, 2))
        ax_overlay.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 2)])
        
        # Time-of-day shading
        ax_overlay.axvspan(0, 6, alpha=0.08, color='navy')
        ax_overlay.axvspan(9, 12, alpha=0.08, color='orange')
        ax_overlay.axvspan(18, 22, alpha=0.08, color='purple')
        
        # Vertical cursor line and markers
        self.vline_overlay = ax_overlay.axvline(x=0, color='red', linewidth=1.5, 
                                                linestyle='--', visible=False, zorder=5)
        self.markers_overlay = {}
        for _, device in self.device_config.iterrows():
            if device['enabled']:
                marker, = ax_overlay.plot([], [], 'o', color=device['color'], 
                                         markersize=6, markeredgecolor='white', 
                                         markeredgewidth=1.5, visible=False, zorder=10)
                self.markers_overlay[device['device']] = marker
        
        # WiFi band chart
        ax_bands = fig.add_subplot(gs[1, :])
        
        band_colors = {'2.4GHz': '#FF6B9D', '5GHz': '#4ECDC4', '6GHz': '#95E1D3'}
        
        ax_bands.fill_between(self.hours, 0, self.wifi_band_data['2.4GHz'],
                             color=band_colors['2.4GHz'], alpha=0.7, label='2.4 GHz (WiFi 4/5/6)')
        
        base = self.wifi_band_data['2.4GHz'].copy()
        ax_bands.fill_between(self.hours, base, base + self.wifi_band_data['5GHz'],
                             color=band_colors['5GHz'], alpha=0.7, label='5 GHz (WiFi 5/6/6E)')
        
        base += self.wifi_band_data['5GHz']
        ax_bands.fill_between(self.hours, base, base + self.wifi_band_data['6GHz'],
                             color=band_colors['6GHz'], alpha=0.7, label='6 GHz (WiFi 6E)')
        
        ax_bands.set_ylabel('Bandwidth (Mbps)', fontsize=12, fontweight='bold')
        ax_bands.set_title('WiFi Band Utilization', fontsize=14, fontweight='bold')
        ax_bands.legend(loc='upper left', framealpha=0.95, fontsize=11)
        ax_bands.grid(True, alpha=0.3, linestyle='--')
        ax_bands.set_xlim(0, 24)
        ax_bands.set_xticks(range(0, 25, 2))
        ax_bands.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 2)])
        
        self.vline_bands = ax_bands.axvline(x=0, color='red', linewidth=1.5, 
                                            linestyle='--', visible=False, zorder=5)
        
        self.info_box_overlay = ax_overlay.text(0.02, 0.98, '', transform=ax_overlay.transAxes,
                                               fontsize=9, verticalalignment='top',
                                               bbox=dict(boxstyle='round,pad=0.8', 
                                                        facecolor='lightyellow', 
                                                        edgecolor='black', 
                                                        linewidth=1.5, alpha=0.95),
                                               visible=False, zorder=100,
                                               fontfamily='monospace')
        
        self.info_box_bands = ax_bands.text(0.02, 0.98, '', transform=ax_bands.transAxes,
                                            fontsize=9, verticalalignment='top',
                                            bbox=dict(boxstyle='round,pad=0.8', 
                                                     facecolor='lightcyan', 
                                                     edgecolor='black', 
                                                     linewidth=1.5, alpha=0.95),
                                            visible=False, zorder=100,
                                            fontfamily='monospace')
        
        # Individual device breakouts
        devices = [d for d in ['laptop', 'smartphone', 'tablet', 'smartwatch'] 
                  if self.device_config[self.device_config['device'] == d]['enabled'].iloc[0]]
        
        for idx, device in enumerate(devices):
            if idx >= 4:
                break
            row = 2 + idx // 2
            col = idx % 2
            ax = fig.add_subplot(gs[row, col])
            
            device_info = self.device_config[self.device_config['device'] == device].iloc[0]
            data = self.bandwidth_data[device]
            
            ax.fill_between(self.hours, 0, data, color=device_info['color'], alpha=0.5)
            ax.plot(self.hours, data, color=device_info['color'], linewidth=2)
            
            ax.set_title(f"{device_info['display_name']}", 
                        fontsize=11, fontweight='bold', pad=12)
            ax.set_xlabel('Time of Day', fontsize=9, labelpad=8)
            ax.set_ylabel('Mbps', fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, 24)
            ax.set_xticks(range(0, 25, 6))
            ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 6)], fontsize=8)
            
            avg = np.mean(data)
            peak = np.max(data)
            ax.text(0.02, 0.98, f'Avg: {avg:.1f} Mbps\nPeak: {peak:.1f} Mbps',
                   transform=ax.transAxes, fontsize=8,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        plt.suptitle('24-Hour College Student Bandwidth & WiFi Analysis - v15', 
                    fontsize=16, fontweight='bold', y=0.995)
        
        self.fig = fig
        self.ax_overlay = ax_overlay
        self.ax_bands = ax_bands
        
        fig.canvas.mpl_connect('motion_notify_event', self._on_hover)
        
        return fig
    
    def _on_hover(self, event):
        """Handle mouse hover events"""
        if event.inaxes == self.ax_overlay:
            x = event.xdata
            if x is not None and 0 <= x < 24:
                idx = min(int(x * 2), 47)
                
                self.vline_overlay.set_xdata([x, x])
                self.vline_overlay.set_visible(True)
                
                for device_name, marker in self.markers_overlay.items():
                    y_val = self.bandwidth_data[device_name][idx]
                    marker.set_data([x], [y_val])
                    marker.set_visible(True)
                
                total = self.get_total_bandwidth()[idx]
                text = f"⏰ {int(x):02d}:{int((x % 1) * 60):02d}\n━━━━━━━━━━━━━━━━\nTotal: {total:.1f} Mbps\n\n"
                
                for device in ['laptop', 'smartphone', 'tablet', 'smartwatch']:
                    device_info = self.device_config[self.device_config['device'] == device].iloc[0]
                    if device_info['enabled']:
                        val = self.bandwidth_data[device][idx]
                        text += f"{'💻' if device=='laptop' else '📱' if device in ['smartphone','tablet'] else '⌚'} "
                        text += f"{device_info['display_name']}: {val:5.1f} Mbps\n"
                
                text += f"━━━━━━━━━━━━━━━━\n🎯 {self.activities[idx]}"
                
                self.info_box_overlay.set_text(text)
                self.info_box_overlay.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                self._hide_overlay_elements()
        
        elif event.inaxes == self.ax_bands:
            x = event.xdata
            if x is not None and 0 <= x < 24:
                idx = min(int(x * 2), 47)
                
                self.vline_bands.set_xdata([x, x])
                self.vline_bands.set_visible(True)
                
                band_24 = self.wifi_band_data['2.4GHz'][idx]
                band_5 = self.wifi_band_data['5GHz'][idx]
                band_6 = self.wifi_band_data['6GHz'][idx]
                total_bands = band_24 + band_5 + band_6
                
                time_str = f"{int(x):02d}:{int((x % 1) * 60):02d}"
                text = f"⏰ {time_str}\n━━━━━━━━━━━━━━━━\nTotal: {total_bands:.1f} Mbps\n\n"
                text += f"📡 2.4GHz: {band_24:5.1f} Mbps ({band_24/total_bands*100:4.1f}%)\n"
                text += f"📡 5GHz:   {band_5:5.1f} Mbps ({band_5/total_bands*100:4.1f}%)\n"
                text += f"📡 6GHz:   {band_6:5.1f} Mbps ({band_6/total_bands*100:4.1f}%)\n"
                text += f"━━━━━━━━━━━━━━━━\n🎯 {self.activities[idx]}"
                
                self.info_box_bands.set_text(text)
                self.info_box_bands.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                self._hide_bands_elements()
        else:
            self._hide_overlay_elements()
            self._hide_bands_elements()
    
    def _hide_overlay_elements(self):
        self.vline_overlay.set_visible(False)
        for marker in self.markers_overlay.values():
            marker.set_visible(False)
        self.info_box_overlay.set_visible(False)
        self.fig.canvas.draw_idle()
    
    def _hide_bands_elements(self):
        self.vline_bands.set_visible(False)
        self.info_box_bands.set_visible(False)
        self.fig.canvas.draw_idle()
    
    def export_html(self, filename='bandwidth_report.html'):
        """Export current data as interactive HTML visualization"""
        import json
        
        laptop_data = self.bandwidth_data['laptop'].tolist()
        smartphone_data = self.bandwidth_data['smartphone'].tolist()
        tablet_data = self.bandwidth_data['tablet'].tolist()
        smartwatch_data = self.bandwidth_data['smartwatch'].tolist()
        
        band_24_data = self.wifi_band_data['2.4GHz'].tolist()
        band_5_data = self.wifi_band_data['5GHz'].tolist()
        band_6_data = self.wifi_band_data['6GHz'].tolist()
        
        stats = self.get_statistics()
        time_labels = [f"{int(h):02d}:{int((h % 1) * 60):02d}" for h in self.hours]
        activities_json = json.dumps(self.activities)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>24-Hour College Student Bandwidth Analysis v15</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
        }}
        h1 {{ text-align: center; color: #2d3748; margin-bottom: 10px; font-size: 2.5em; }}
        .subtitle {{ text-align: center; color: #718096; margin-bottom: 30px; font-size: 1.1em; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 12px;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stat-label {{ font-size: 0.9em; opacity: 0.9; margin-bottom: 5px; }}
        .stat-value {{ font-size: 2em; font-weight: bold; }}
        .chart-section {{
            margin-bottom: 40px;
            background: #f7fafc;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .chart-title {{ font-size: 1.4em; color: #2d3748; margin-bottom: 15px; font-weight: 600; }}
        .chart-container {{ position: relative; height: 400px; margin-bottom: 20px; }}
        .small-charts {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}
        .small-chart-container {{ background: #f7fafc; padding: 20px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .small-chart-title {{ font-size: 1.1em; color: #2d3748; margin-bottom: 10px; font-weight: 600; }}
        .small-chart-wrapper {{ position: relative; height: 250px; }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #e2e8f0;
            color: #718096;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 24-Hour College Student Bandwidth Analysis</h1>
        <p class="subtitle">WiFi 6/6E Multi-Device Usage Profile - v15 DataFrame Edition</p>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">Peak Bandwidth</div><div class="stat-value">{stats['peak_bandwidth']:.1f} Mbps</div></div>
            <div class="stat-card"><div class="stat-label">Average Bandwidth</div><div class="stat-value">{stats['average_bandwidth']:.1f} Mbps</div></div>
            <div class="stat-card"><div class="stat-label">Daily Data Usage</div><div class="stat-value">{stats['total_daily_data_gb']:.1f} GB</div></div>
            <div class="stat-card"><div class="stat-label">Active Devices</div><div class="stat-value">4</div></div>
        </div>
        <div class="chart-section"><div class="chart-title">Device Bandwidth Overlay</div><div class="chart-container"><canvas id="overlayChart"></canvas></div></div>
        <div class="chart-section"><div class="chart-title">WiFi Band Utilization</div><div class="chart-container"><canvas id="bandChart"></canvas></div></div>
        <div class="small-charts">
            <div class="small-chart-container"><div class="small-chart-title">💻 Laptop</div><div class="small-chart-wrapper"><canvas id="laptopChart"></canvas></div></div>
            <div class="small-chart-container"><div class="small-chart-title">📱 Smartphone</div><div class="small-chart-wrapper"><canvas id="smartphoneChart"></canvas></div></div>
            <div class="small-chart-container"><div class="small-chart-title">📱 Tablet</div><div class="small-chart-wrapper"><canvas id="tabletChart"></canvas></div></div>
            <div class="small-chart-container"><div class="small-chart-title">⌚ Smartwatch</div><div class="small-chart-wrapper"><canvas id="smartwatchChart"></canvas></div></div>
        </div>
        <div class="footer">Generated from CollegeStudentBandwidthModel v15 Python Analysis<br>DataFrame-based configuration with CSV import/export</div>
    </div>
    <script>
        const timeLabels={json.dumps(time_labels)};const laptopData={json.dumps(laptop_data)};const smartphoneData={json.dumps(smartphone_data)};const tabletData={json.dumps(tablet_data)};const smartwatchData={json.dumps(smartwatch_data)};const band24Data={json.dumps(band_24_data)};const band5Data={json.dumps(band_5_data)};const band6Data={json.dumps(band_6_data)};const activities={activities_json};
        const verticalLinePlugin={{id:'verticalLine',afterDraw:(chart)=>{{if(chart.tooltip?._active?.length){{const ctx=chart.ctx;const activePoint=chart.tooltip._active[0];const x=activePoint.element.x;const topY=chart.scales.y.top;const bottomY=chart.scales.y.bottom;ctx.save();ctx.beginPath();ctx.moveTo(x,topY);ctx.lineTo(x,bottomY);ctx.lineWidth=2;ctx.strokeStyle='rgba(255,0,0,0.7)';ctx.setLineDash([5,5]);ctx.stroke();ctx.restore();}}}}}};
        Chart.register(verticalLinePlugin);
        Chart.Tooltip.positioners.dynamic=function(elements,eventPosition){{const chart=this.chart;const chartArea=chart.chartArea;const chartWidth=chartArea.right-chartArea.left;const midpoint=chartArea.left+(chartWidth/2);if(eventPosition.x<midpoint){{return{{x:eventPosition.x+20,y:chartArea.top+10,xAlign:'left',yAlign:'top'}};}}else{{return{{x:eventPosition.x-20,y:chartArea.top+10,xAlign:'right',yAlign:'top'}};}}}};
        const commonOptions={{responsive:true,maintainAspectRatio:false,interaction:{{mode:'index',intersect:false}},plugins:{{legend:{{display:false}},tooltip:{{enabled:true,position:'dynamic',backgroundColor:'rgba(0,0,0,0.9)',padding:12,titleFont:{{size:13,weight:'bold'}},bodyFont:{{size:12,family:'Courier New'}},displayColors:true,boxWidth:8,boxHeight:8,callbacks:{{title:(items)=>`⏰ ${{items[0].label}}`}}}}}},scales:{{x:{{grid:{{color:'rgba(0,0,0,0.05)'}},ticks:{{callback:function(value,index){{return index%4===0?this.getLabelForValue(value):''}}}}}},y:{{grid:{{color:'rgba(0,0,0,0.05)'}},beginAtZero:true}}}}}};
        new Chart(document.getElementById('overlayChart'),{{type:'line',data:{{labels:timeLabels,datasets:[{{label:'Laptop',data:laptopData,borderColor:'#4ECDC4',backgroundColor:'rgba(78,205,196,0.1)',borderWidth:3,pointRadius:0,pointHoverRadius:6,pointHoverBackgroundColor:'#4ECDC4',pointHoverBorderColor:'white',pointHoverBorderWidth:2,tension:0.4}},{{label:'Smartphone',data:smartphoneData,borderColor:'#FF6B6B',backgroundColor:'rgba(255,107,107,0.1)',borderWidth:3,pointRadius:0,pointHoverRadius:6,pointHoverBackgroundColor:'#FF6B6B',pointHoverBorderColor:'white',pointHoverBorderWidth:2,tension:0.4}},{{label:'Tablet',data:tabletData,borderColor:'#45B7D1',backgroundColor:'rgba(69,183,209,0.1)',borderWidth:3,pointRadius:0,pointHoverRadius:6,pointHoverBackgroundColor:'#45B7D1',pointHoverBorderColor:'white',pointHoverBorderWidth:2,tension:0.4}},{{label:'Smartwatch',data:smartwatchData,borderColor:'#FFA07A',backgroundColor:'rgba(255,160,122,0.1)',borderWidth:3,borderDash:[5,5],pointRadius:0,pointHoverRadius:6,pointHoverBackgroundColor:'#FFA07A',pointHoverBorderColor:'white',pointHoverBorderWidth:2,tension:0.4}}]}},options:{{...commonOptions,plugins:{{...commonOptions.plugins,legend:{{display:true,position:'top',labels:{{padding:15,font:{{size:12}}}}}},tooltip:{{...commonOptions.plugins.tooltip,callbacks:{{title:(items)=>`⏰ ${{items[0].label}}`,afterTitle:(items)=>'━━━━━━━━━━━━━━━━',label:(context)=>`${{context.dataset.label}}: ${{context.parsed.y.toFixed(2)}} Mbps`,afterBody:(items)=>{{const idx=items[0].dataIndex;const total=laptopData[idx]+smartphoneData[idx]+tabletData[idx]+smartwatchData[idx];return `\\n━━━━━━━━━━━━━━━━\\nTotal: ${{total.toFixed(1)}} Mbps\\n━━━━━━━━━━━━━━━━\\n🎯 ${{activities[idx]}}`}}}}}}}}}}}});
        new Chart(document.getElementById('bandChart'),{{type:'line',data:{{labels:timeLabels,datasets:[{{label:'2.4 GHz',data:band24Data,borderColor:'#FF6B9D',backgroundColor:'rgba(255,107,157,0.6)',borderWidth:2,fill:true,pointRadius:0,pointHoverRadius:5,tension:0.4}},{{label:'5 GHz',data:band5Data,borderColor:'#4ECDC4',backgroundColor:'rgba(78,205,196,0.6)',borderWidth:2,fill:true,pointRadius:0,pointHoverRadius:5,tension:0.4}},{{label:'6 GHz',data:band6Data,borderColor:'#95E1D3',backgroundColor:'rgba(149,225,211,0.6)',borderWidth:2,fill:true,pointRadius:0,pointHoverRadius:5,tension:0.4}}]}},options:{{...commonOptions,plugins:{{...commonOptions.plugins,legend:{{display:true,position:'top',labels:{{padding:15,font:{{size:12}}}}}},tooltip:{{...commonOptions.plugins.tooltip,callbacks:{{title:(items)=>`⏰ ${{items[0].label}}`,afterTitle:(items)=>'━━━━━━━━━━━━━━━━',label:(context)=>{{const total=band24Data[context.dataIndex]+band5Data[context.dataIndex]+band6Data[context.dataIndex];const percent=(context.parsed.y/total*100).toFixed(1);return `${{context.dataset.label}}: ${{context.parsed.y.toFixed(1)}} Mbps (${{percent}}%)`}},afterBody:(items)=>{{const idx=items[0].dataIndex;return `\\n━━━━━━━━━━━━━━━━\\n🎯 ${{activities[idx]}}`}}}}}}}},scales:{{...commonOptions.scales,y:{{...commonOptions.scales.y,stacked:true}}}}}}}});
        const createDeviceChart=(canvasId,data,color,label)=>{{new Chart(document.getElementById(canvasId),{{type:'line',data:{{labels:timeLabels,datasets:[{{label:label,data:data,borderColor:color,backgroundColor:color+'40',borderWidth:2,fill:true,pointRadius:0,pointHoverRadius:5,pointHoverBackgroundColor:color,pointHoverBorderColor:'white',pointHoverBorderWidth:2,tension:0.4}}]}},options:{{...commonOptions,plugins:{{...commonOptions.plugins,tooltip:{{...commonOptions.plugins.tooltip,callbacks:{{title:(items)=>'⏰ '+items[0].label,label:(context)=>context.parsed.y.toFixed(2)+' Mbps',afterLabel:(context)=>{{const avg=data.reduce((a,b)=>a+b)/data.length;const max=Math.max(...data);return '\\nAvg: '+avg.toFixed(2)+' Mbps\\nPeak: '+max.toFixed(2)+' Mbps'}}}}}}}}}}}})}}}};
        createDeviceChart('laptopChart',laptopData,'#4ECDC4','Laptop');
        createDeviceChart('smartphoneChart',smartphoneData,'#FF6B6B','Smartphone');
        createDeviceChart('tabletChart',tabletData,'#45B7D1','Tablet');
        createDeviceChart('smartwatchChart',smartwatchData,'#FFA07A','Smartwatch');
    </script>
</body>
</html>"""
        
        with open(filename, 'w') as f:
            f.write(html_content)
        
        print(f"\n✅ HTML report exported to: {filename}")
        print(f"📊 Open in browser to view interactive visualization")


# Example usage
if __name__ == "__main__":
    import sys
    
    def print_menu():
        print("\n" + "=" * 70)
        print("COLLEGE STUDENT BANDWIDTH MODEL v15 - Interactive Menu")
        print("=" * 70)
        print("\n📊 ANALYSIS & VISUALIZATION")
        print("  1. Run Full Analysis (Statistics + Charts + HTML)")
        print("  2. Print Statistics Only")
        print("  3. Show Data Tables Summary")
        print("  4. Generate Matplotlib Charts")
        print("  5. Export HTML Report")
        
        print("\n📤 EXPORT DATA")
        print("  6. Export Device Configuration to CSV")
        print("  7. Export Usage Parameters to CSV")
        print("  8. Export Application Bandwidth to CSV")
        print("  9. Export Time-Series Data to CSV")
        print(" 10. Export ALL Data to CSV (with timestamp)")
        
        print("\n📥 IMPORT DATA")
        print(" 11. Import Device Configuration from CSV")
        print(" 12. Import Usage Parameters from CSV")
        print(" 13. Import Application Bandwidth from CSV")
        
        print("\n⚙️  CONFIGURATION")
        print(" 14. View Current Device Configuration")
        print(" 15. Enable/Disable Specific Device")
        print(" 16. Modify Device Parameters")
        
        print("\n🔄 SCENARIOS")
        print(" 17. Save Current Configuration as Scenario")
        print(" 18. Load Scenario from File")
        print(" 19. List Available Scenarios")
        
        print("\n❌ EXIT")
        print("  0. Exit Program")
        
        print("\n" + "=" * 70)
    
    def get_user_input(prompt, input_type=str, default=None):
        """Get validated user input"""
        while True:
            try:
                user_input = input(prompt)
                if not user_input and default is not None:
                    return default
                return input_type(user_input)
            except ValueError:
                print(f"❌ Invalid input. Please enter a valid {input_type.__name__}.")
    
    def modify_device_menu(model):
        """Interactive device modification"""
        print("\n" + "=" * 70)
        print("MODIFY DEVICE PARAMETERS")
        print("=" * 70)
        print("\nCurrent Devices:")
        for idx, row in model.device_config.iterrows():
            status = "✅" if row['enabled'] else "❌"
            print(f"  {idx + 1}. {status} {row['display_name']} - {row['wifi_capability']}")
        
        device_num = get_user_input("\nSelect device number (0 to cancel): ", int, 0)
        if device_num == 0 or device_num > len(model.device_config):
            return
        
        device_idx = device_num - 1
        device = model.device_config.iloc[device_idx]
        
        print(f"\nModifying: {device['display_name']}")
        print("Leave blank to keep current value")
        
        new_max_bw = get_user_input(f"Max bandwidth [{device['max_bandwidth_mbps']} Mbps]: ", float, device['max_bandwidth_mbps'])
        new_typical_bw = get_user_input(f"Typical usage [{device['typical_usage_mbps']} Mbps]: ", float, device['typical_usage_mbps'])
        new_count = get_user_input(f"Device count [{device['device_count']}]: ", int, device['device_count'])
        
        model.device_config.at[device_idx, 'max_bandwidth_mbps'] = new_max_bw
        model.device_config.at[device_idx, 'typical_usage_mbps'] = new_typical_bw
        model.device_config.at[device_idx, 'device_count'] = new_count
        
        # Regenerate data
        model.bandwidth_data = model._generate_bandwidth_data()
        model.wifi_band_data = model._generate_wifi_band_data()
        model.timeseries_df = model._create_timeseries_dataframe()
        
        print(f"\n✅ {device['display_name']} parameters updated!")
    
    def enable_disable_device_menu(model):
        """Interactive device enable/disable"""
        print("\n" + "=" * 70)
        print("ENABLE/DISABLE DEVICES")
        print("=" * 70)
        print("\nCurrent Devices:")
        for idx, row in model.device_config.iterrows():
            status = "✅ ENABLED" if row['enabled'] else "❌ DISABLED"
            print(f"  {idx + 1}. {status} - {row['display_name']}")
        
        device_num = get_user_input("\nSelect device number to toggle (0 to cancel): ", int, 0)
        if device_num == 0 or device_num > len(model.device_config):
            return
        
        device_idx = device_num - 1
        current_status = model.device_config.at[device_idx, 'enabled']
        model.device_config.at[device_idx, 'enabled'] = not current_status
        
        # Regenerate data
        model.bandwidth_data = model._generate_bandwidth_data()
        model.wifi_band_data = model._generate_wifi_band_data()
        model.timeseries_df = model._create_timeseries_dataframe()
        
        device_name = model.device_config.iloc[device_idx]['display_name']
        new_status = "ENABLED" if not current_status else "DISABLED"
        print(f"\n✅ {device_name} is now {new_status}")
    
    def save_scenario_menu(model):
        """Save current configuration as a scenario"""
        print("\n" + "=" * 70)
        print("SAVE SCENARIO")
        print("=" * 70)
        scenario_name = get_user_input("\nEnter scenario name: ", str)
        if not scenario_name:
            print("❌ Scenario name cannot be empty")
            return
        
        # Clean filename
        clean_name = "".join(c for c in scenario_name if c.isalnum() or c in (' ', '_', '-')).strip()
        clean_name = clean_name.replace(' ', '_')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        prefix = f"scenario_{clean_name}_{timestamp}"
        
        model.export_device_config(f'{prefix}_devices.csv')
        model.export_usage_params(f'{prefix}_usage.csv')
        model.export_app_bandwidth(f'{prefix}_apps.csv')
        
        print(f"\n✅ Scenario saved with prefix: {prefix}")
        print(f"   Files: {prefix}_devices.csv, {prefix}_usage.csv, {prefix}_apps.csv")
    
    def load_scenario_menu(model):
        """Load a scenario from files"""
        print("\n" + "=" * 70)
        print("LOAD SCENARIO")
        print("=" * 70)
        
        # List available scenario files
        import glob
        device_files = sorted(glob.glob("scenario_*_devices.csv"), reverse=True)
        
        if not device_files:
            print("❌ No scenario files found")
            print("   Scenarios should be named: scenario_NAME_TIMESTAMP_devices.csv")
            return
        
        print("\nAvailable scenarios:")
        for idx, filename in enumerate(device_files[:10], 1):  # Show last 10
            print(f"  {idx}. {filename}")
        
        file_num = get_user_input("\nSelect scenario number (0 to cancel): ", int, 0)
        if file_num == 0 or file_num > len(device_files):
            return
        
        selected_file = device_files[file_num - 1]
        base_name = selected_file.replace('_devices.csv', '')
        
        # Load all related files
        try:
            model.import_device_config(f'{base_name}_devices.csv')
            
            # Try to load other files if they exist
            try:
                model.import_usage_params(f'{base_name}_usage.csv')
            except FileNotFoundError:
                pass
            
            try:
                model.import_app_bandwidth(f'{base_name}_apps.csv')
            except FileNotFoundError:
                pass
            
            print(f"\n✅ Scenario loaded: {base_name}")
        except Exception as e:
            print(f"❌ Error loading scenario: {e}")
    
    def list_scenarios_menu():
        """List all available scenarios"""
        print("\n" + "=" * 70)
        print("AVAILABLE SCENARIOS")
        print("=" * 70)
        
        import glob
        device_files = sorted(glob.glob("scenario_*_devices.csv"), reverse=True)
        
        if not device_files:
            print("\n❌ No scenarios found")
            return
        
        print(f"\nFound {len(device_files)} scenario(s):\n")
        for filename in device_files:
            # Extract info from filename
            parts = filename.replace('scenario_', '').replace('_devices.csv', '').split('_')
            if len(parts) >= 2:
                timestamp = parts[-2] + '_' + parts[-1]
                name = '_'.join(parts[:-2]) if len(parts) > 2 else parts[0]
                print(f"  📁 {name}")
                print(f"     Date: {timestamp[:8]} Time: {timestamp[9:]}")
                print(f"     File: {filename}\n")
        
        input("\nPress Enter to continue...")
    
    # Main interactive loop
    model = CollegeStudentBandwidthModel()
    
    print("\n" + "=" * 70)
    print("🎓 COLLEGE STUDENT BANDWIDTH MODEL v15")
    print("=" * 70)
    print("\nWelcome to the interactive bandwidth modeling tool!")
    print("This tool helps you analyze and visualize WiFi usage patterns.")
    
    while True:
        print_menu()
        choice = get_user_input("\nEnter your choice: ", str, "0")
        
        try:
            if choice == "0":
                print("\n👋 Thanks for using the Bandwidth Model! Goodbye.")
                sys.exit(0)
            
            elif choice == "1":
                print("\n🔄 Running full analysis...")
                model.print_statistics()
                model.plot_overlaid_devices()
                model.export_html('bandwidth_report_v15.html')
                plt.draw()
                plt.pause(0.1)
                print("\n✅ Analysis complete! Charts displayed (close chart windows to continue)")
                input("\nPress Enter when ready to continue...")
                plt.close('all')
            
            elif choice == "2":
                model.print_statistics()
            
            elif choice == "3":
                model.print_dataframe_summary()
                input("\nPress Enter to continue...")
            
            elif choice == "4":
                print("\n📊 Generating charts...")
                model.plot_overlaid_devices()
                plt.draw()
                plt.pause(0.1)
                print("\n✅ Charts displayed (close chart windows to continue)")
                input("\nPress Enter when ready to continue...")
                plt.close('all')
            
            elif choice == "5":
                filename = get_user_input("Enter HTML filename [bandwidth_report_v15.html]: ", str, "bandwidth_report_v15.html")
                model.export_html(filename)
            
            elif choice == "6":
                filename = get_user_input("Enter filename [device_config.csv]: ", str, "device_config.csv")
                model.export_device_config(filename)
            
            elif choice == "7":
                filename = get_user_input("Enter filename [usage_params.csv]: ", str, "usage_params.csv")
                model.export_usage_params(filename)
            
            elif choice == "8":
                filename = get_user_input("Enter filename [app_bandwidth.csv]: ", str, "app_bandwidth.csv")
                model.export_app_bandwidth(filename)
            
            elif choice == "9":
                filename = get_user_input("Enter filename [timeseries_data.csv]: ", str, "timeseries_data.csv")
                model.export_timeseries(filename)
            
            elif choice == "10":
                prefix = get_user_input("Enter prefix [bandwidth_model]: ", str, "bandwidth_model")
                model.export_all_data(prefix)
            
            elif choice == "11":
                filename = get_user_input("Enter CSV filename: ", str)
                if filename:
                    model.import_device_config(filename)
            
            elif choice == "12":
                filename = get_user_input("Enter CSV filename: ", str)
                if filename:
                    model.import_usage_params(filename)
            
            elif choice == "13":
                filename = get_user_input("Enter CSV filename: ", str)
                if filename:
                    model.import_app_bandwidth(filename)
            
            elif choice == "14":
                print("\n" + "=" * 70)
                print("CURRENT DEVICE CONFIGURATION")
                print("=" * 70)
                print(model.device_config.to_string(index=False))
                input("\nPress Enter to continue...")
            
            elif choice == "15":
                enable_disable_device_menu(model)
            
            elif choice == "16":
                modify_device_menu(model)
            
            elif choice == "17":
                save_scenario_menu(model)
            
            elif choice == "18":
                load_scenario_menu(model)
            
            elif choice == "19":
                list_scenarios_menu()
            
            else:
                print("\n❌ Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or report this issue.")
