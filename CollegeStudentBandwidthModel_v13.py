# v13 latest

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
            'smartphone': {'color': '#FF6B6B', 'label': 'Smartphone', 'line_style': '-'},
            'laptop': {'color': '#4ECDC4', 'label': 'Laptop', 'line_style': '-'},
            'tablet': {'color': '#45B7D1', 'label': 'Tablet', 'line_style': '-'},
            'smartwatch': {'color': '#FFA07A', 'label': 'Smartwatch', 'line_style': '--'}
        }
        
        # Initialize bandwidth data
        self.bandwidth_data = self._generate_bandwidth_data()
        self.wifi_band_data = self._generate_wifi_band_data()
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
    
    def _generate_wifi_band_data(self):
        """Generate WiFi band usage data (2.4GHz, 5GHz, 6GHz) across 24 hours"""
        # Initialize with zeros
        band_data = {
            '2.4GHz': np.zeros(48),
            '5GHz': np.zeros(48),
            '6GHz': np.zeros(48)
        }
        
        for i in range(48):
            hour = i / 2.0
            
            # Smartwatch always on 2.4GHz
            band_data['2.4GHz'][i] += self.bandwidth_data['smartwatch'][i]
            
            # Smartphone: 5GHz most of the time, 6GHz for heavy usage
            phone_bw = self.bandwidth_data['smartphone'][i]
            if phone_bw > 8:  # Heavy usage -> 6GHz
                band_data['6GHz'][i] += phone_bw
            else:
                band_data['5GHz'][i] += phone_bw
            
            # Laptop: Prefers 6GHz for high bandwidth, 5GHz otherwise
            laptop_bw = self.bandwidth_data['laptop'][i]
            if laptop_bw > 15:  # 4K streaming, gaming -> 6GHz
                band_data['6GHz'][i] += laptop_bw
            elif laptop_bw > 5:  # Normal work -> 5GHz
                band_data['5GHz'][i] += laptop_bw
            else:  # Low usage/sleep -> 2.4GHz (lower power)
                band_data['2.4GHz'][i] += laptop_bw
            
            # Tablet: WiFi 6 capable (5GHz), uses 2.4GHz when idle
            tablet_bw = self.bandwidth_data['tablet'][i]
            if tablet_bw > 3:
                band_data['5GHz'][i] += tablet_bw
            else:
                band_data['2.4GHz'][i] += tablet_bw
            
            # During gym time (15:00-16:00), phone may use 2.4GHz for better range
            if 15 <= hour < 16:
                # Move phone from 5GHz to 2.4GHz
                if phone_bw <= 8:
                    band_data['5GHz'][i] -= phone_bw
                    band_data['2.4GHz'][i] += phone_bw
        
        return band_data
    
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
    
    def plot_overlaid_devices(self, figsize=(16, 12)):
        """Create visualization with overlaid device lines and WiFi band breakdown"""
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(4, 2, height_ratios=[2.5, 2.5, 1.5, 1], hspace=0.35, wspace=0.3)
        
        # Main overlaid plot - all in absolute Mbps
        ax_overlay = fig.add_subplot(gs[0, :])
        
        # Store line objects for hover interaction
        self.device_lines = {}
        
        # Plot each device as overlay with same scale (Mbps)
        for device in ['laptop', 'smartphone', 'tablet', 'smartwatch']:
            color = self.devices[device]['color']
            label = self.devices[device]['label']
            style = self.devices[device]['line_style']
            data = self.bandwidth_data[device]
            
            if device == 'smartwatch':
                # Thicker line for visibility despite low values
                line, = ax_overlay.plot(self.hours, data, color=color, 
                              linewidth=3, alpha=0.9, label=label, linestyle=style)
            else:
                line, = ax_overlay.plot(self.hours, data, color=color, 
                              linewidth=2.5, alpha=0.8, label=label, linestyle=style)
            
            self.device_lines[device] = line
        
        ax_overlay.set_ylabel('Bandwidth (Mbps)', fontsize=12, fontweight='bold')
        ax_overlay.set_title('Device Bandwidth Overlay - All Devices in Mbps', 
                           fontsize=14, fontweight='bold')
        ax_overlay.legend(loc='upper left', framealpha=0.95, fontsize=11)
        ax_overlay.grid(True, alpha=0.3, linestyle='--')
        ax_overlay.set_xlim(0, 24)
        ax_overlay.set_xticks(range(0, 25, 2))
        ax_overlay.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 2)])
        
        # Add time-of-day shading
        ax_overlay.axvspan(0, 6, alpha=0.08, color='navy')
        ax_overlay.axvspan(9, 12, alpha=0.08, color='orange')
        ax_overlay.axvspan(18, 22, alpha=0.08, color='purple')
        
        # Create vertical cursor line and marker dots for overlay chart
        self.vline_overlay = ax_overlay.axvline(x=0, color='red', linewidth=1.5, 
                                                linestyle='--', visible=False, zorder=5)
        self.markers_overlay = {}
        for device in ['laptop', 'smartphone', 'tablet', 'smartwatch']:
            marker, = ax_overlay.plot([], [], 'o', color=self.devices[device]['color'], 
                                     markersize=6, markeredgecolor='white', 
                                     markeredgewidth=1.5, visible=False, zorder=10)
            self.markers_overlay[device] = marker
        
        # WiFi band stacked area chart
        ax_bands = fig.add_subplot(gs[1, :])
        
        band_colors = {
            '2.4GHz': '#FF6B9D',
            '5GHz': '#4ECDC4',
            '6GHz': '#95E1D3'
        }
        
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
        
        # Create vertical cursor line for band chart
        self.vline_bands = ax_bands.axvline(x=0, color='red', linewidth=1.5, 
                                            linestyle='--', visible=False, zorder=5)
        
        # Create info text boxes for each chart
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
        
        # Individual device breakouts (2x2 grid)
        devices = ['laptop', 'smartphone', 'tablet', 'smartwatch']
        
        for idx, device in enumerate(devices):
            row = 2 + idx // 2
            col = idx % 2
            ax = fig.add_subplot(gs[row, col])
            
            data = self.bandwidth_data[device]
            color = self.devices[device]['color']
            
            ax.fill_between(self.hours, 0, data, color=color, alpha=0.5)
            ax.plot(self.hours, data, color=color, linewidth=2)
            
            ax.set_title(f"{self.devices[device]['label']}", 
                        fontsize=11, fontweight='bold', pad=12)
            ax.set_xlabel('Time of Day', fontsize=9, labelpad=8)
            ax.set_ylabel('Mbps', fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, 24)
            ax.set_xticks(range(0, 25, 6))
            ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 6)], fontsize=8)
            
            # Add statistics
            avg = np.mean(data)
            peak = np.max(data)
            ax.text(0.02, 0.98, f'Avg: {avg:.1f} Mbps\nPeak: {peak:.1f} Mbps',
                   transform=ax.transAxes, fontsize=8,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        plt.suptitle('24-Hour College Student Bandwidth & WiFi Analysis', 
                    fontsize=16, fontweight='bold', y=0.995)
        
        # Store axes for hover functionality
        self.fig = fig
        self.ax_overlay = ax_overlay
        self.ax_bands = ax_bands
        
        # Connect hover event
        fig.canvas.mpl_connect('motion_notify_event', self._on_hover)
        
        return fig
    
    def _on_hover(self, event):
        """Handle mouse hover events with vertical line and markers"""
        # Check if hovering over overlay chart
        if event.inaxes == self.ax_overlay:
            x = event.xdata
            if x is not None and 0 <= x < 24:
                # Find closest time slot
                idx = min(int(x * 2), 47)
                
                # Show vertical line
                self.vline_overlay.set_xdata([x, x])
                self.vline_overlay.set_visible(True)
                
                # Update markers for each device
                for device in ['laptop', 'smartphone', 'tablet', 'smartwatch']:
                    y_val = self.bandwidth_data[device][idx]
                    self.markers_overlay[device].set_data([x], [y_val])
                    self.markers_overlay[device].set_visible(True)
                
                # Get bandwidth values
                total = self.get_total_bandwidth()[idx]
                laptop = self.bandwidth_data['laptop'][idx]
                phone = self.bandwidth_data['smartphone'][idx]
                tablet = self.bandwidth_data['tablet'][idx]
                watch = self.bandwidth_data['smartwatch'][idx]
                
                # Format info text
                time_str = f"{int(x):02d}:{int((x % 1) * 60):02d}"
                text = f"⏰ {time_str}\n"
                text += f"━━━━━━━━━━━━━━━━\n"
                text += f"Total: {total:.1f} Mbps\n\n"
                text += f"💻 Laptop:  {laptop:5.1f} Mbps\n"
                text += f"📱 Phone:   {phone:5.1f} Mbps\n"
                text += f"📱 Tablet:  {tablet:5.1f} Mbps\n"
                text += f"⌚ Watch:   {watch:5.2f} Mbps\n"
                text += f"━━━━━━━━━━━━━━━━\n"
                text += f"🎯 {self.activities[idx]}"
                
                self.info_box_overlay.set_text(text)
                self.info_box_overlay.set_visible(True)
                
                self.fig.canvas.draw_idle()
            else:
                self._hide_overlay_elements()
        
        # Check if hovering over band chart
        elif event.inaxes == self.ax_bands:
            x = event.xdata
            if x is not None and 0 <= x < 24:
                # Find closest time slot
                idx = min(int(x * 2), 47)
                
                # Show vertical line
                self.vline_bands.set_xdata([x, x])
                self.vline_bands.set_visible(True)
                
                # Get WiFi band info
                band_24 = self.wifi_band_data['2.4GHz'][idx]
                band_5 = self.wifi_band_data['5GHz'][idx]
                band_6 = self.wifi_band_data['6GHz'][idx]
                total_bands = band_24 + band_5 + band_6
                
                # Format info text
                time_str = f"{int(x):02d}:{int((x % 1) * 60):02d}"
                text = f"⏰ {time_str}\n"
                text += f"━━━━━━━━━━━━━━━━\n"
                text += f"Total: {total_bands:.1f} Mbps\n\n"
                text += f"📡 2.4GHz: {band_24:5.1f} Mbps ({band_24/total_bands*100:4.1f}%)\n"
                text += f"📡 5GHz:   {band_5:5.1f} Mbps ({band_5/total_bands*100:4.1f}%)\n"
                text += f"📡 6GHz:   {band_6:5.1f} Mbps ({band_6/total_bands*100:4.1f}%)\n"
                text += f"━━━━━━━━━━━━━━━━\n"
                text += f"🎯 {self.activities[idx]}"
                
                self.info_box_bands.set_text(text)
                self.info_box_bands.set_visible(True)
                
                self.fig.canvas.draw_idle()
            else:
                self._hide_bands_elements()
        
        # If not hovering over either chart, hide everything
        else:
            self._hide_overlay_elements()
            self._hide_bands_elements()
    
    def _hide_overlay_elements(self):
        """Hide overlay chart hover elements"""
        self.vline_overlay.set_visible(False)
        for marker in self.markers_overlay.values():
            marker.set_visible(False)
        self.info_box_overlay.set_visible(False)
        self.fig.canvas.draw_idle()
    
    def _hide_bands_elements(self):
        """Hide band chart hover elements"""
        self.vline_bands.set_visible(False)
        self.info_box_bands.set_visible(False)
        self.fig.canvas.draw_idle()
    
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
            },
            'wifi_band_usage': {
                band: {
                    'average_mbps': np.mean(data),
                    'peak_mbps': np.max(data),
                    'percentage_of_total': (np.sum(data) / np.sum(total)) * 100
                }
                for band, data in self.wifi_band_data.items()
            }
        }
        
        return stats
    
    def print_statistics(self):
        """Print formatted statistics"""
        stats = self.get_statistics()
        
        print("=" * 70)
        print("COLLEGE STUDENT BANDWIDTH ANALYSIS")
        print("=" * 70)
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
        
        print(f"\n📡 WiFi Band Utilization:")
        for band, band_stats in stats['wifi_band_usage'].items():
            print(f"\n  {band}:")
            print(f"    Average: {band_stats['average_mbps']:.2f} Mbps")
            print(f"    Peak: {band_stats['peak_mbps']:.1f} Mbps")
            print(f"    % of Total: {band_stats['percentage_of_total']:.1f}%")
        
        print("\n" + "=" * 70)
    
    def export_html(self, filename='bandwidth_report.html'):
        """Export current data as interactive HTML visualization"""
        import json
        
        # Convert numpy arrays to lists for JSON serialization
        laptop_data = self.bandwidth_data['laptop'].tolist()
        smartphone_data = self.bandwidth_data['smartphone'].tolist()
        tablet_data = self.bandwidth_data['tablet'].tolist()
        smartwatch_data = self.bandwidth_data['smartwatch'].tolist()
        
        band_24_data = self.wifi_band_data['2.4GHz'].tolist()
        band_5_data = self.wifi_band_data['5GHz'].tolist()
        band_6_data = self.wifi_band_data['6GHz'].tolist()
        
        # Get statistics for the summary cards
        stats = self.get_statistics()
        
        # Create time labels
        time_labels = [f"{int(h):02d}:{int((h % 1) * 60):02d}" for h in self.hours]
        
        # Escape activities for JavaScript
        activities_json = json.dumps(self.activities)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>24-Hour College Student Bandwidth Analysis</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
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
        
        h1 {{
            text-align: center;
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        
        .subtitle {{
            text-align: center;
            color: #718096;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        
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
        
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
        }}
        
        .chart-section {{
            margin-bottom: 40px;
            background: #f7fafc;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .chart-title {{
            font-size: 1.4em;
            color: #2d3748;
            margin-bottom: 15px;
            font-weight: 600;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 20px;
        }}
        
        .small-charts {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}
        
        .small-chart-container {{
            background: #f7fafc;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .small-chart-title {{
            font-size: 1.1em;
            color: #2d3748;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .small-chart-wrapper {{
            position: relative;
            height: 250px;
        }}
        
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
        <p class="subtitle">WiFi 6/6E Multi-Device Usage Profile</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Peak Bandwidth</div>
                <div class="stat-value">{stats['peak_bandwidth']:.1f} Mbps</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Average Bandwidth</div>
                <div class="stat-value">{stats['average_bandwidth']:.1f} Mbps</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Daily Data Usage</div>
                <div class="stat-value">{stats['total_daily_data_gb']:.1f} GB</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Active Devices</div>
                <div class="stat-value">4</div>
            </div>
        </div>
        
        <div class="chart-section">
            <div class="chart-title">Device Bandwidth Overlay</div>
            <div class="chart-container">
                <canvas id="overlayChart"></canvas>
            </div>
        </div>
        
        <div class="chart-section">
            <div class="chart-title">WiFi Band Utilization</div>
            <div class="chart-container">
                <canvas id="bandChart"></canvas>
            </div>
        </div>
        
        <div class="small-charts">
            <div class="small-chart-container">
                <div class="small-chart-title">💻 Laptop</div>
                <div class="small-chart-wrapper">
                    <canvas id="laptopChart"></canvas>
                </div>
            </div>
            <div class="small-chart-container">
                <div class="small-chart-title">📱 Smartphone</div>
                <div class="small-chart-wrapper">
                    <canvas id="smartphoneChart"></canvas>
                </div>
            </div>
            <div class="small-chart-container">
                <div class="small-chart-title">📱 Tablet</div>
                <div class="small-chart-wrapper">
                    <canvas id="tabletChart"></canvas>
                </div>
            </div>
            <div class="small-chart-container">
                <div class="small-chart-title">⌚ Smartwatch</div>
                <div class="small-chart-wrapper">
                    <canvas id="smartwatchChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="footer">
            Generated from CollegeStudentBandwidthModel Python Analysis<br>
            Data represents typical 24-hour usage pattern for WiFi 6/6E environment
        </div>
    </div>

    <script>
        // Data from Python analysis
        const timeLabels = {json.dumps(time_labels)};
        const laptopData = {json.dumps(laptop_data)};
        const smartphoneData = {json.dumps(smartphone_data)};
        const tabletData = {json.dumps(tablet_data)};
        const smartwatchData = {json.dumps(smartwatch_data)};
        const band24Data = {json.dumps(band_24_data)};
        const band5Data = {json.dumps(band_5_data)};
        const band6Data = {json.dumps(band_6_data)};
        const activities = {activities_json};
        
        // Chart.js custom plugin for vertical line
        const verticalLinePlugin = {{
            id: 'verticalLine',
            afterDraw: (chart) => {{
                if (chart.tooltip?._active?.length) {{
                    const ctx = chart.ctx;
                    const activePoint = chart.tooltip._active[0];
                    const x = activePoint.element.x;
                    const topY = chart.scales.y.top;
                    const bottomY = chart.scales.y.bottom;
                    
                    ctx.save();
                    ctx.beginPath();
                    ctx.moveTo(x, topY);
                    ctx.lineTo(x, bottomY);
                    ctx.lineWidth = 2;
                    ctx.strokeStyle = 'rgba(255, 0, 0, 0.7)';
                    ctx.setLineDash([5, 5]);
                    ctx.stroke();
                    ctx.restore();
                }}
            }}
        }};
        
        Chart.register(verticalLinePlugin);
        
        // Custom tooltip positioner
        Chart.Tooltip.positioners.dynamic = function(elements, eventPosition) {{
            const chart = this.chart;
            const chartArea = chart.chartArea;
            const chartWidth = chartArea.right - chartArea.left;
            const midpoint = chartArea.left + (chartWidth / 2);
            
            if (eventPosition.x < midpoint) {{
                return {{
                    x: eventPosition.x + 20,
                    y: chartArea.top + 10,
                    xAlign: 'left',
                    yAlign: 'top'
                }};
            }} else {{
                return {{
                    x: eventPosition.x - 20,
                    y: chartArea.top + 10,
                    xAlign: 'right',
                    yAlign: 'top'
                }};
            }}
        }};
        
        // Common chart options
        const commonOptions = {{
            responsive: true,
            maintainAspectRatio: false,
            interaction: {{
                mode: 'index',
                intersect: false,
            }},
            plugins: {{
                legend: {{
                    display: false
                }},
                tooltip: {{
                    enabled: true,
                    position: 'dynamic',
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    padding: 12,
                    titleFont: {{ size: 13, weight: 'bold' }},
                    bodyFont: {{ size: 12, family: 'Courier New' }},
                    displayColors: true,
                    boxWidth: 8,
                    boxHeight: 8,
                    callbacks: {{
                        title: (items) => {{
                            return `⏰ ${{items[0].label}}`;
                        }}
                    }}
                }}
            }},
            scales: {{
                x: {{
                    grid: {{ color: 'rgba(0, 0, 0, 0.05)' }},
                    ticks: {{
                        callback: function(value, index) {{
                            return index % 4 === 0 ? this.getLabelForValue(value) : '';
                        }}
                    }}
                }},
                y: {{
                    grid: {{ color: 'rgba(0, 0, 0, 0.05)' }},
                    beginAtZero: true
                }}
            }}
        }};
        
        // Overlay Chart
        new Chart(document.getElementById('overlayChart'), {{
            type: 'line',
            data: {{
                labels: timeLabels,
                datasets: [
                    {{
                        label: 'Laptop',
                        data: laptopData,
                        borderColor: '#4ECDC4',
                        backgroundColor: 'rgba(78, 205, 196, 0.1)',
                        borderWidth: 3,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        pointHoverBackgroundColor: '#4ECDC4',
                        pointHoverBorderColor: 'white',
                        pointHoverBorderWidth: 2,
                        tension: 0.4
                    }},
                    {{
                        label: 'Smartphone',
                        data: smartphoneData,
                        borderColor: '#FF6B6B',
                        backgroundColor: 'rgba(255, 107, 107, 0.1)',
                        borderWidth: 3,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        pointHoverBackgroundColor: '#FF6B6B',
                        pointHoverBorderColor: 'white',
                        pointHoverBorderWidth: 2,
                        tension: 0.4
                    }},
                    {{
                        label: 'Tablet',
                        data: tabletData,
                        borderColor: '#45B7D1',
                        backgroundColor: 'rgba(69, 183, 209, 0.1)',
                        borderWidth: 3,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        pointHoverBackgroundColor: '#45B7D1',
                        pointHoverBorderColor: 'white',
                        pointHoverBorderWidth: 2,
                        tension: 0.4
                    }},
                    {{
                        label: 'Smartwatch',
                        data: smartwatchData,
                        borderColor: '#FFA07A',
                        backgroundColor: 'rgba(255, 160, 122, 0.1)',
                        borderWidth: 3,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        pointHoverBackgroundColor: '#FFA07A',
                        pointHoverBorderColor: 'white',
                        pointHoverBorderWidth: 2,
                        tension: 0.4
                    }}
                ]
            }},
            options: {{
                ...commonOptions,
                plugins: {{
                    ...commonOptions.plugins,
                    legend: {{
                        display: true,
                        position: 'top',
                        labels: {{ padding: 15, font: {{ size: 12 }} }}
                    }},
                    tooltip: {{
                        ...commonOptions.plugins.tooltip,
                        callbacks: {{
                            title: (items) => `⏰ ${{items[0].label}}`,
                            afterTitle: (items) => '━━━━━━━━━━━━━━━━',
                            label: (context) => {{
                                return `${{context.dataset.label}}: ${{context.parsed.y.toFixed(2)}} Mbps`;
                            }},
                            afterBody: (items) => {{
                                const idx = items[0].dataIndex;
                                const total = laptopData[idx] + smartphoneData[idx] + tabletData[idx] + smartwatchData[idx];
                                return `\\n━━━━━━━━━━━━━━━━\\nTotal: ${{total.toFixed(1)}} Mbps\\n━━━━━━━━━━━━━━━━\\n🎯 ${{activities[idx]}}`;
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Band Chart
        new Chart(document.getElementById('bandChart'), {{
            type: 'line',
            data: {{
                labels: timeLabels,
                datasets: [
                    {{
                        label: '2.4 GHz',
                        data: band24Data,
                        borderColor: '#FF6B9D',
                        backgroundColor: 'rgba(255, 107, 157, 0.6)',
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        tension: 0.4
                    }},
                    {{
                        label: '5 GHz',
                        data: band5Data,
                        borderColor: '#4ECDC4',
                        backgroundColor: 'rgba(78, 205, 196, 0.6)',
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        tension: 0.4
                    }},
                    {{
                        label: '6 GHz',
                        data: band6Data,
                        borderColor: '#95E1D3',
                        backgroundColor: 'rgba(149, 225, 211, 0.6)',
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        tension: 0.4
                    }}
                ]
            }},
            options: {{
                ...commonOptions,
                plugins: {{
                    ...commonOptions.plugins,
                    legend: {{
                        display: true,
                        position: 'top',
                        labels: {{ padding: 15, font: {{ size: 12 }} }}
                    }},
                    tooltip: {{
                        ...commonOptions.plugins.tooltip,
                        callbacks: {{
                            title: (items) => `⏰ ${{items[0].label}}`,
                            afterTitle: (items) => '━━━━━━━━━━━━━━━━',
                            label: (context) => {{
                                const total = band24Data[context.dataIndex] + band5Data[context.dataIndex] + band6Data[context.dataIndex];
                                const percent = (context.parsed.y / total * 100).toFixed(1);
                                return `${{context.dataset.label}}: ${{context.parsed.y.toFixed(1)}} Mbps (${{percent}}%)`;
                            }},
                            afterBody: (items) => {{
                                const idx = items[0].dataIndex;
                                return `\\n━━━━━━━━━━━━━━━━\\n🎯 ${{activities[idx]}}`;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    ...commonOptions.scales,
                    y: {{
                        ...commonOptions.scales.y,
                        stacked: true
                    }}
                }}
            }}
        }});
        
        // Individual device charts
        const createDeviceChart = (canvasId, data, color, label) => {{
            new Chart(document.getElementById(canvasId), {{
                type: 'line',
                data: {{
                    labels: timeLabels,
                    datasets: [{{
                        label: label,
                        data: data,
                        borderColor: color,
                        backgroundColor: color + '40',
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        pointHoverBackgroundColor: color,
                        pointHoverBorderColor: 'white',
                        pointHoverBorderWidth: 2,
                        tension: 0.4
                    }}]
                }},
                options: {{
                    ...commonOptions,
                    plugins: {{
                        ...commonOptions.plugins,
                        tooltip: {{
                            ...commonOptions.plugins.tooltip,
                            callbacks: {{
                                title: (items) => `⏰ ${{items[0].label}}`,
                                label: (context) => `${{context.parsed.y.toFixed(2)}} Mbps`,
                                afterLabel: (context) => {{
                                    const avg = data.reduce((a,b) => a+b) / data.length;
                                    const max = Math.max(...data);
                                    return `\\nAvg: ${{avg.toFixed(2)}} Mbps\\nPeak: ${{max.toFixed(2)}} Mbps`;
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }};
        
        createDeviceChart('laptopChart', laptopData, '#4ECDC4', 'Laptop');
        createDeviceChart('smartphoneChart', smartphoneData, '#FF6B6B', 'Smartphone');
        createDeviceChart('tabletChart', tabletData, '#45B7D1', 'Tablet');
        createDeviceChart('smartwatchChart', smartwatchData, '#FFA07A', 'Smartwatch');
    </script>
</body>
</html>"""
        
        with open(filename, 'w') as f:
            f.write(html_content)
        
        print(f"\n✅ HTML report exported to: {filename}")
        print(f"📊 Open in browser to view interactive visualization")


# Example usage and demo
if __name__ == "__main__":
    # Create model instance
    model = CollegeStudentBandwidthModel()
    
    # Print statistics
    model.print_statistics()
    
    # Create visualizations
    print("\n" + "=" * 70)
    print("GENERATING VISUALIZATION")
    print("=" * 70)
    
    print("\nCreating bandwidth and WiFi band analysis...")
    fig = model.plot_overlaid_devices()
    
    # Export HTML report
    print("\n" + "=" * 70)
    print("EXPORTING HTML REPORT")
    print("=" * 70)
    model.export_html('bandwidth_report.html')
    
    # Show plots
    plt.show()
    
    print("\n✅ Analysis complete!")
    print("💡 Hover over charts to see detailed activity and WiFi band info")
    print("📊 All devices shown in absolute Mbps values for easy comparison")
    print("🌐 HTML report ready for customer presentations")
