import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates
from datetime import datetime, timedelta

class CollegeStudentBandwidthModel:
    """
    Models 24-hour bandwidth consumption for a college student with multiple devices.
    Can be used standalone or integrated into larger network planning tools.
    """
    
    def __init__(self):
        self.hours = np.arange(0, 24, 0.5)  # 30-minute intervals (48 points)
        self.devices = {
            'smartphone': {'color': '#FF6B6B', 'label': 'Smartphone'},
            'laptop': {'color': '#4ECDC4', 'label': 'Laptop'},
            'tablet': {'color': '#45B7D1', 'label': 'Tablet'},
            'smartwatch': {'color': '#FFA07A', 'label': 'Smartwatch'}
        }
        
        # Initialize bandwidth data
        self.bandwidth_data = self._generate_bandwidth_data()
        self.activities = self._generate_activity_descriptions()
        
    def _generate_bandwidth_data(self):
        """Generate bandwidth consumption data for each device across 24 hours"""
        data = {}
        
        # Smartphone bandwidth (Mbps) - highly variable throughout day
        smartphone = np.array([
            # 00:00-06:00 (Sleep)
            1, 0.5, 0.3, 0.2, 0.2, 0.3, 2, 3, 5, 4, 8, 12,
            # 06:00-12:00 (Wake up, class)
            10, 8, 5, 3, 2, 1.5, 1, 1.5, 2, 5, 10, 8,
            # 12:00-18:00 (Lunch, study, gym)
            12, 15, 8, 4, 3, 2, 3, 2.5, 2, 1.5, 3, 4,
            # 18:00-24:00 (Evening social/entertainment)
            5, 8, 10, 12, 8, 6, 10, 12, 8, 10, 8, 6
        ])
        
        # Laptop bandwidth (Mbps) - peaks during work/streaming
        laptop = np.array([
            # 00:00-06:00 (Sleep/streaming late)
            20, 15, 0.5, 0.3, 0.3, 0.5, 1, 0.8, 1, 2, 3, 5,
            # 06:00-12:00 (Morning prep, classes)
            8, 12, 15, 8, 5, 4, 6, 10, 8, 12, 10, 6,
            # 12:00-18:00 (Lunch video, library study)
            12, 10, 8, 15, 18, 12, 8, 10, 12, 8, 5, 3,
            # 18:00-24:00 (Heavy usage - homework, streaming, gaming)
            15, 20, 25, 22, 18, 12, 8, 10, 15, 20, 22, 20
        ])
        
        # Tablet bandwidth (Mbps) - supplemental device
        tablet = np.array([
            # 00:00-06:00 (Sleep/updates)
            1, 2, 1.5, 1, 0.5, 0.5, 0.3, 0.2, 0.2, 0.3, 1, 2,
            # 06:00-12:00 (Morning check, class notes)
            3, 2, 1, 0.5, 0.3, 2, 3, 2.5, 2, 3, 2, 1.5,
            # 12:00-18:00 (Reading, study)
            2, 3, 4, 3, 2.5, 2, 1.5, 1, 0.5, 0.3, 2, 4,
            # 18:00-24:00 (Light evening use, streaming)
            3, 5, 8, 10, 6, 4, 2, 3, 8, 12, 10, 8
        ])
        
        # Smartwatch bandwidth (Mbps) - consistent low usage
        smartwatch = np.array([
            # 00:00-06:00 (Sleep tracking)
            0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.02, 0.05, 0.08, 0.1,
            # 06:00-12:00 (Morning sync, notifications)
            0.15, 0.12, 0.5, 0.3, 0.1, 0.08, 0.1, 0.15, 0.1, 0.08, 0.06, 0.05,
            # 12:00-18:00 (Activity tracking)
            0.08, 0.1, 0.08, 0.06, 0.05, 0.1, 0.25, 0.3, 0.2, 0.15, 0.1, 0.08,
            # 18:00-24:00 (Evening notifications)
            0.1, 0.12, 0.15, 0.1, 0.08, 0.06, 0.05, 0.08, 0.1, 0.06, 0.04, 0.02
        ])
        
        data['smartphone'] = smartphone
        data['laptop'] = laptop
        data['tablet'] = tablet
        data['smartwatch'] = smartwatch
        
        return data
    
    def _generate_activity_descriptions(self):
        """Generate detailed activity descriptions for each time slot"""
        activities = []
        
        # 00:00-06:00
        activities.extend([
            "00:00 - Streaming Netflix 4K in bed (Laptop)\nMessaging friends (Phone)\nSleep prep (Watch)",
            "00:30 - Finishing movie, winding down\nLate night social media scroll (Phone)",
            "01:00 - Devices entering sleep mode\nCloud photo backup starting (Phone)",
            "01:30 - Deep sleep mode\nBackground system updates (Laptop)",
            "02:00 - Sleep tracking active (Watch)\nScheduled cloud backup (Phone, Tablet)",
            "02:30 - Minimal network activity\nPeriodic sync checks",
            "03:00 - Deep sleep continues\niCloud/Google backup window (Phone)",
            "03:30 - Background maintenance\nApp updates downloading",
            "04:00 - Continued backup sync\nOS updates (Laptop)",
            "04:30 - Low activity period\nBackup completion",
            "05:00 - Pre-wake prep\nCalendar/email pre-sync",
            "05:30 - System wake routines\nWeather/news cache update"
        ])
        
        # 06:00-12:00
        activities.extend([
            "06:00 - ALARM! First phone check in bed\nEmail sync, Instagram scroll, news apps",
            "06:30 - Getting ready routine\nSpotify streaming (Phone)\nMorning health sync (Watch)",
            "07:00 - Breakfast time\nPodcast listening\nBackground app refresh",
            "07:30 - Pre-class prep begins\nDownloading lecture slides (Laptop)\nLMS access, Canvas/Blackboard",
            "08:00 - Reviewing notes\nPDF textbook download (Tablet)\nClass schedule check (Phone)",
            "08:30 - Walking to class\nTransition to campus WiFi\nMusic streaming continues",
            "09:00 - First lecture starts\nCloud note-taking (Laptop: Google Docs)\nDigital textbook (Tablet)",
            "09:30 - Lecture continues\nReference materials lookup\nLecture recording stream",
            "10:00 - Class wrapping up\nSaving notes to cloud\nQuick email check",
            "10:30 - BREAK - Coffee & social media\nInstagram, TikTok, Snapchat (Phone)\nHeavy short-form video",
            "11:00 - Second class (Discussion seminar)\nCollaborative doc editing\nScreen share viewing",
            "11:30 - Active class participation\nReal-time research during discussion\nFact-checking"
        ])
        
        # 12:00-18:00
        activities.extend([
            "12:00 - Lunch at dining hall\nYouTube videos while eating (Phone)\nSocial media catch-up",
            "12:30 - Lunch continues\nGroup chat conversations\nPlanning afternoon",
            "13:00 - Library study session begins\nAcademic database research (Laptop)\nJSTOR, PubMed access",
            "13:30 - Deep research mode\nPDF journal downloads\nReference manager sync",
            "14:00 - Writing research paper\nGoogle Docs collaboration\nSpotify background music",
            "14:30 - Continued writing\nMultiple reference tabs open\nCitation management",
            "15:00 - Gym time!\nFitness tracking (Watch)\nWorkout app sync",
            "15:30 - Workout continues\nMusic streaming (mostly offline)\nQuick social checks between sets",
            "16:00 - Post-gym, heading back\nCampus to dorm WiFi transition\nMusic continues",
            "16:30 - Quick shower\nDevices reconnecting to dorm WiFi\nDay's data syncing",
            "17:00 - Homework starts\nVideo tutorials (YouTube EDU)\nCoding environment active",
            "17:30 - Intensive project work\nMultiple browser tabs\nCloud storage sync"
        ])
        
        # 18:00-24:00
        activities.extend([
            "18:00 - Homework continues\nGitHub activity\nMulti-device productivity",
            "18:30 - Dinner time!\nNetflix/YouTube during meal\nTexting friends",
            "19:00 - Dinner entertainment\nStreaming content\nSocial media browsing",
            "19:30 - Study group video call\nZoom/Discord 1080p\nScreen sharing, collaborative docs",
            "20:00 - Video call continues\nNote-taking during call\nShared presentations",
            "20:30 - Call wrapping up\nFinalizing group notes\nScheduling next session",
            "21:00 - Social/Gaming hour\nOnline gaming OR Reddit/YouTube\nDiscord voice chat",
            "21:30 - Continued gaming/social\nHeavy social media\nCasual mobile games (Tablet)",
            "22:00 - Evening wind-down\n4K streaming (Netflix/Prime/Disney+)\nMessaging friends",
            "22:30 - Binge watching continues\nTwitch stream alternative\nLast social checks",
            "23:00 - Pre-sleep routine\nFinal TikTok/Instagram scroll\nMeditation app",
            "23:30 - Getting ready for bed\nSetting alarms\nDevices moving to sleep mode"
        ])
        
        return activities
    
    def get_total_bandwidth(self):
        """Calculate total bandwidth across all devices"""
        total = np.zeros_like(self.hours)
        for device in self.bandwidth_data.values():
            total += device
        return total
    
    def plot_interactive(self, figsize=(16, 10)):
        """Create interactive visualization with hover annotations"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, height_ratios=[3, 1])
        
        # Plot 1: Stacked area chart
        ax1.fill_between(self.hours, 0, self.bandwidth_data['smartwatch'], 
                         color=self.devices['smartwatch']['color'], 
                         alpha=0.7, label=self.devices['smartwatch']['label'])
        
        base = self.bandwidth_data['smartwatch'].copy()
        ax1.fill_between(self.hours, base, base + self.bandwidth_data['tablet'], 
                         color=self.devices['tablet']['color'], 
                         alpha=0.7, label=self.devices['tablet']['label'])
        
        base += self.bandwidth_data['tablet']
        ax1.fill_between(self.hours, base, base + self.bandwidth_data['smartphone'], 
                         color=self.devices['smartphone']['color'], 
                         alpha=0.7, label=self.devices['smartphone']['label'])
        
        base += self.bandwidth_data['smartphone']
        ax1.fill_between(self.hours, base, base + self.bandwidth_data['laptop'], 
                         color=self.devices['laptop']['color'], 
                         alpha=0.7, label=self.devices['laptop']['label'])
        
        # Add individual device lines for clarity
        laptop_line = self.bandwidth_data['smartwatch'] + self.bandwidth_data['tablet'] + \
                      self.bandwidth_data['smartphone'] + self.bandwidth_data['laptop']
        smartphone_line = self.bandwidth_data['smartwatch'] + self.bandwidth_data['tablet'] + \
                          self.bandwidth_data['smartphone']
        tablet_line = self.bandwidth_data['smartwatch'] + self.bandwidth_data['tablet']
        
        ax1.plot(self.hours, laptop_line, color=self.devices['laptop']['color'], 
                linewidth=1.5, alpha=0.8)
        ax1.plot(self.hours, smartphone_line, color=self.devices['smartphone']['color'], 
                linewidth=1.5, alpha=0.8)
        ax1.plot(self.hours, tablet_line, color=self.devices['tablet']['color'], 
                linewidth=1.5, alpha=0.8)
        
        # Styling
        ax1.set_ylabel('Bandwidth Consumption (Mbps)', fontsize=12, fontweight='bold')
        ax1.set_title('24-Hour College Student Bandwidth Profile\nWiFi 6/6E Multi-Device Usage', 
                     fontsize=14, fontweight='bold', pad=20)
        ax1.legend(loc='upper left', framealpha=0.9, fontsize=10)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_xlim(0, 24)
        ax1.set_ylim(0, max(self.get_total_bandwidth()) * 1.1)
        
        # Add time-of-day shading
        ax1.axvspan(0, 6, alpha=0.1, color='navy', label='_Sleep')
        ax1.axvspan(9, 12, alpha=0.1, color='orange', label='_Classes')
        ax1.axvspan(18, 22, alpha=0.1, color='purple', label='_Peak Evening')
        
        # Add peak markers
        total = self.get_total_bandwidth()
        peak_indices = [np.argmax(total[i*2:(i+1)*2]) + i*2 for i in range(12)]
        major_peaks = sorted(peak_indices, key=lambda i: total[i], reverse=True)[:3]
        
        for peak in major_peaks:
            ax1.plot(self.hours[peak], total[peak], 'r*', markersize=15, 
                    markeredgecolor='darkred', markeredgewidth=1.5)
        
        # Plot 2: Total bandwidth overview
        total_bandwidth = self.get_total_bandwidth()
        ax2.fill_between(self.hours, 0, total_bandwidth, color='#2C3E50', alpha=0.6)
        ax2.plot(self.hours, total_bandwidth, color='#2C3E50', linewidth=2)
        
        ax2.set_xlabel('Time of Day (24-hour)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Total (Mbps)', fontsize=10, fontweight='bold')
        ax2.set_title('Aggregate Bandwidth Consumption', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_xlim(0, 24)
        ax2.set_ylim(0, max(total_bandwidth) * 1.1)
        
        # Format x-axis
        for ax in [ax1, ax2]:
            ax.set_xticks(range(0, 25, 2))
            ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 2)], rotation=45)
        
        # Add annotation capability (static version - shows on click would need interactive backend)
        self.annotation = ax1.annotate('', xy=(0, 0), xytext=(20, 20),
                                       textcoords='offset points',
                                       bbox=dict(boxstyle='round,pad=0.8', fc='yellow', alpha=0.9),
                                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
                                       fontsize=9, visible=False, zorder=10)
        
        # Connect hover event
        fig.canvas.mpl_connect('motion_notify_event', 
                              lambda event: self._on_hover(event, ax1))
        
        plt.tight_layout()
        return fig, (ax1, ax2)
    
    def _on_hover(self, event, ax):
        """Handle mouse hover events to show activity details"""
        if event.inaxes == ax:
            x = event.xdata
            if x is not None and 0 <= x <= 24:
                # Find closest time slot
                idx = int(x * 2)  # Convert to 30-min intervals
                if idx >= len(self.activities):
                    idx = len(self.activities) - 1
                
                # Get bandwidth values
                total = self.get_total_bandwidth()[idx]
                laptop = self.bandwidth_data['laptop'][idx]
                phone = self.bandwidth_data['smartphone'][idx]
                tablet = self.bandwidth_data['tablet'][idx]
                watch = self.bandwidth_data['smartwatch'][idx]
                
                # Format annotation text
                time_str = f"{int(x):02d}:{int((x % 1) * 60):02d}"
                text = f"Time: {time_str}\n"
                text += f"Total: {total:.1f} Mbps\n\n"
                text += f"📱 Phone: {phone:.1f} Mbps\n"
                text += f"💻 Laptop: {laptop:.1f} Mbps\n"
                text += f"📱 Tablet: {tablet:.1f} Mbps\n"
                text += f"⌚ Watch: {watch:.2f} Mbps\n\n"
                text += f"{self.activities[idx]}"
                
                self.annotation.set_text(text)
                self.annotation.xy = (x, total)
                self.annotation.set_visible(True)
                ax.figure.canvas.draw_idle()
            else:
                self.annotation.set_visible(False)
                ax.figure.canvas.draw_idle()
    
    def plot_device_comparison(self, figsize=(14, 8)):
        """Create separate plots for each device"""
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
        devices = ['laptop', 'smartphone', 'tablet', 'smartwatch']
        
        for idx, device in enumerate(devices):
            ax = axes[idx]
            data = self.bandwidth_data[device]
            color = self.devices[device]['color']
            
            ax.fill_between(self.hours, 0, data, color=color, alpha=0.6)
            ax.plot(self.hours, data, color=color, linewidth=2)
            
            ax.set_title(f"{self.devices[device]['label']} Bandwidth", 
                        fontsize=12, fontweight='bold')
            ax.set_xlabel('Time of Day', fontsize=10)
            ax.set_ylabel('Mbps', fontsize=10)
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, 24)
            ax.set_xticks(range(0, 25, 4))
            ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 4)])
            
            # Add statistics
            avg = np.mean(data)
            peak = np.max(data)
            ax.text(0.02, 0.98, f'Avg: {avg:.1f} Mbps\nPeak: {peak:.1f} Mbps',
                   transform=ax.transAxes, fontsize=9,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.suptitle('Individual Device Bandwidth Profiles', 
                    fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        return fig, axes
    
    def get_statistics(self):
        """Calculate and return key statistics"""
        total = self.get_total_bandwidth()
        
        stats = {
            'peak_bandwidth': np.max(total),
            'peak_time': self.hours[np.argmax(total)],
            'average_bandwidth': np.mean(total),
            'total_daily_data_gb': np.sum(total) * 0.5 * 3600 / (8 * 1024),  # Convert to GB
            'device_contributions': {
                device: {
                    'average_mbps': np.mean(data),
                    'peak_mbps': np.max(data),
                    'percentage_of_total': (np.sum(data) / np.sum(total)) * 100
                }
                for device, data in self.bandwidth_data.items()
            }
        }
        
        return stats
    
    def print_statistics(self):
        """Print formatted statistics"""
        stats = self.get_statistics()
        
        print("=" * 60)
        print("COLLEGE STUDENT BANDWIDTH ANALYSIS")
        print("=" * 60)
        print(f"\n📊 Overall Statistics:")
        print(f"  Peak Bandwidth: {stats['peak_bandwidth']:.1f} Mbps at {int(stats['peak_time']):02d}:{int((stats['peak_time'] % 1) * 60):02d}")
        print(f"  Average Bandwidth: {stats['average_bandwidth']:.1f} Mbps")
        print(f"  Estimated Daily Data: {stats['total_daily_data_gb']:.1f} GB")
        
        print(f"\n📱 Device Breakdown:")
        for device, device_stats in stats['device_contributions'].items():
            print(f"\n  {self.devices[device]['label']}:")
            print(f"    Average: {device_stats['average_mbps']:.2f} Mbps")
            print(f"    Peak: {device_stats['peak_mbps']:.1f} Mbps")
            print(f"    % of Total: {device_stats['percentage_of_total']:.1f}%")
        
        print("\n" + "=" * 60)


# Example usage and demo
if __name__ == "__main__":
    # Create model instance
    model = CollegeStudentBandwidthModel()
    
    # Print statistics
    model.print_statistics()
    
    # Create visualizations
    print("\nGenerating interactive visualization...")
    fig1, axes1 = model.plot_interactive()
    
    print("Generating device comparison plots...")
    fig2, axes2 = model.plot_device_comparison()
    
    # Show plots
    plt.show()
    
    print("\n✅ Visualization complete!")
    print("💡 Hover over the main chart to see detailed activity information")
    print("⭐ Red stars indicate peak bandwidth periods")
