import pywifi
from pywifi import PyWiFi, const
import time
import platform
from colorama import init, Fore, Style
import sys
import os
from datetime import datetime
import json
import webbrowser

init()

def scan_wifi():
    if platform.system() != "Windows":
        print(f"{Fore.RED}This script only supports Windows.{Style.RESET_ALL}")
        sys.exit(1)
        
    wifi = PyWiFi()
    interfaces = wifi.interfaces()

    if not interfaces:
        print(f"{Fore.RED}No Wi-Fi interfaces found! Ensure Wi-Fi is enabled.{Style.RESET_ALL}")
        print("On Windows, ensure Location Services are enabled (Settings > Privacy > Location).")
        return None

    iface = interfaces[0]
    print(f"{Fore.CYAN}Using interface: {iface.name()}{Style.RESET_ALL}")

    try:
        iface.scan()
        print(f"{Fore.CYAN}Scanning for networks...{Style.RESET_ALL}")
        time.sleep(2)
        networks = iface.scan_results()
    except Exception as e:
        print(f"{Fore.RED}Scan failed: {e}{Style.RESET_ALL}")
        print("Try enabling Location Services or running as Administrator.")
        return None

    if not networks:
        print(f"{Fore.YELLOW}No networks found. Check Wi-Fi status.{Style.RESET_ALL}")
        return None

    # Debug network objects
    if networks and len(networks) > 0:
        print(f"{Fore.GREEN}DEBUG: First network object information:{Style.RESET_ALL}")
        print(f"Type: {type(networks[0])}")
        print(f"Available attributes: {dir(networks[0])}")
        print(f"Raw freq value: {networks[0].freq}")
        print(f"Freq type: {type(networks[0].freq)}")
        
    print(f"{Fore.GREEN}{'SSID':<30} {'Frequency (MHz)':<15} {'Channel':<10} {'Signal (dBm)':<15} {'Security':<15}{Style.RESET_ALL}")
    print("-" * 85)

    network_data = []
    for network in networks:
        ssid = network.ssid if network.ssid else "<Hidden>"
        
        # Debug the raw frequency before conversion
        print(f"Raw frequency for {ssid}: {network.freq}")
        
        frequency = network.freq
        if frequency > 1000:  # If > 1000, probably in kHz
            frequency = frequency // 1000  # Convert kHz to MHz
        
        channel = freq_to_channel(frequency)
        signal = network.signal
        security = get_security_type(network)

        print(f"{ssid:<30} {frequency:<15} {channel:<10} {signal:<15} {security:<15}")
        
        network_data.append({
            'ssid': ssid,
            'frequency': frequency,
            'channel': channel,
            'signal': signal,
            'security': security
        })
    
    return network_data

def get_security_type(network):
    """Determine security type of network."""
    try:
        auth_type = network.akm[0] if hasattr(network, 'akm') and network.akm else const.AKM_TYPE_NONE
        
        if auth_type == const.AKM_TYPE_NONE:
            return "Open"
        elif auth_type == const.AKM_TYPE_WPA:
            return "WPA"
        elif auth_type == const.AKM_TYPE_WPAPSK:
            return "WPA-PSK"
        elif auth_type == const.AKM_TYPE_WPA2:
            return "WPA2"
        elif auth_type == const.AKM_TYPE_WPA2PSK:
            return "WPA2-PSK"
        else:
            return "Unknown"
    except:
        return "Unknown"

def freq_to_channel(frequency):
    # Raw frequency value logging with more info
    print(f"{Fore.CYAN}DEBUG - Network frequency: {frequency} MHz{Style.RESET_ALL}")
    
    # Simplified direct mapping approach
    # 2.4 GHz band
    if 2412 <= frequency <= 2484:
        if frequency == 2412: return 1
        if frequency == 2417: return 2
        if frequency == 2422: return 3
        if frequency == 2427: return 4
        if frequency == 2432: return 5
        if frequency == 2437: return 6
        if frequency == 2442: return 7
        if frequency == 2447: return 8
        if frequency == 2452: return 9
        if frequency == 2457: return 10
        if frequency == 2462: return 11
        if frequency == 2467: return 12
        if frequency == 2472: return 13
        if frequency == 2484: return 14
        
        # If exact match not found but in 2.4GHz range
        return f"~{int((frequency - 2412) / 5) + 1}"
    
    # 5 GHz band - common channels
    if frequency == 5180: return 36
    if frequency == 5200: return 40
    if frequency == 5220: return 44
    if frequency == 5240: return 48
    if frequency == 5260: return 52
    if frequency == 5280: return 56
    if frequency == 5300: return 60
    if frequency == 5320: return 64
    if frequency == 5500: return 100
    if frequency == 5520: return 104
    if frequency == 5745: return 149
    if frequency == 5765: return 153
    if frequency == 5785: return 157
    if frequency == 5805: return 161
    if frequency == 5825: return 165
    
    # Broader 5GHz range check
    if 5170 <= frequency <= 5825:
        return f"~{int((frequency - 5180) / 5) + 36}"
    
    # Fallback 
    print(f"{Fore.YELLOW}WARNING: Could not map frequency {frequency} MHz to a channel{Style.RESET_ALL}")
    return str(frequency) + "MHz"  # Return the frequency itself to diagnose

def get_security_badge_color(security):
    """Return Tailwind CSS classes for security badge colors."""
    if security == "Open":
        return "bg-red-600 text-gray-100"
    elif security.startswith("WPA2"):
        return "bg-green-600 text-gray-100"
    elif security.startswith("WPA"):
        return "bg-yellow-600 text-gray-100"
    else:
        return "bg-gray-600 text-gray-100"

def generate_html_report(networks):
    """Generate a beautiful HTML report with Tailwind CSS."""
    if not networks:
        print(f"{Fore.RED}No network data to generate report.{Style.RESET_ALL}")
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"wifi_scan_report_{timestamp}.html"
    
    # Create HTML content with Tailwind CSS
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wi-Fi Scan Report - {timestamp}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{}}
            }}
        }}
    </script>
</head>
<body class="bg-gray-900 text-gray-200 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <div class="bg-gray-800 shadow-lg rounded-lg overflow-hidden">
            <div class="bg-gradient-to-r from-blue-900 to-indigo-900 px-6 py-4">
                <div class="flex justify-between items-center">
                    <h1 class="text-white text-2xl font-bold">Wi-Fi Networks Scan Report</h1>
                    <div class="text-gray-300 text-sm">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
                </div>
                <div class="text-blue-200 mt-1">
                    <p>Windows {platform.version()}</p>
                    <p>Networks: {len(networks)}</p>
                </div>
            </div>
            
            <!-- Channel Distribution Graph at the top -->
            <div class="p-6 bg-gray-800">
                <h2 class="text-xl font-semibold mb-4 text-white">Channel Utilization</h2>
                <div class="w-full h-[250px]">
                    <canvas id="topChannelChart"></canvas>
                </div>
            </div>
            
            <div class="p-6">
                <div class="flex justify-between mb-4">
                    <button onclick="window.print()" class="bg-blue-700 hover:bg-blue-800 text-white px-4 py-2 rounded shadow">
                        Print Report
                    </button>
                    <div class="flex space-x-2">
                        <button onclick="sortTable('signal', 'desc')" class="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded shadow text-white">
                            Sort by Signal
                        </button>
                        <button onclick="sortTable('channel', 'asc')" class="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded shadow text-white">
                            Sort by Channel
                        </button>
                    </div>
                </div>
                
                <div class="overflow-x-auto">
                    <table id="networkTable" class="min-w-full bg-gray-800 border border-gray-700">
                        <thead>
                            <tr class="bg-gray-700">
                                <th class="px-6 py-3 border-b border-gray-600 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">
                                    SSID
                                </th>
                                <th class="px-6 py-3 border-b border-gray-600 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">
                                    Frequency (MHz)
                                </th>
                                <th class="px-6 py-3 border-b border-gray-600 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">
                                    Channel
                                </th>
                                <th class="px-6 py-3 border-b border-gray-600 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">
                                    Signal (dBm)
                                </th>
                                <th class="px-6 py-3 border-b border-gray-600 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">
                                    Security
                                </th>
                                <th class="px-6 py-3 border-b border-gray-600 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">
                                    Signal Strength
                                </th>
                            </tr>
                        </thead>
                        <tbody>
"""
    
    # Add network rows
    for i, network in enumerate(networks):
        ssid = network['ssid']
        frequency = network['frequency']
        channel = network['channel']
        signal = network['signal']
        security = network['security']
        
        # Determine signal strength and color
        signal_class = ""
        signal_width = "0%"
        signal_strength = "Unknown"
        
        if isinstance(signal, (int, float)):
            if signal >= -50:
                signal_class = "bg-green-500"
                signal_strength = "Excellent"
                signal_width = "100%"
            elif signal >= -60:
                signal_class = "bg-green-400"
                signal_strength = "Good"
                signal_width = "80%"
            elif signal >= -70:
                signal_class = "bg-yellow-400"
                signal_strength = "Fair"
                signal_width = "60%"
            elif signal >= -80:
                signal_class = "bg-orange-400"
                signal_strength = "Weak"
                signal_width = "40%"
            else:
                signal_class = "bg-red-500"
                signal_strength = "Poor"
                signal_width = "20%"
        
        row_class = "bg-gray-800" if i % 2 == 0 else "bg-gray-750"
        html_content += f"""
                            <tr class="{row_class} hover:bg-gray-700">
                                <td class="px-6 py-4 whitespace-nowrap border-b border-gray-600">
                                    <div class="text-sm font-medium text-gray-200">{ssid}</div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap border-b border-gray-600">
                                    <div class="text-sm text-gray-300">{frequency}</div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap border-b border-gray-600">
                                    <div class="text-sm text-gray-300">{channel}</div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap border-b border-gray-600">
                                    <div class="text-sm text-gray-300">{signal}</div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap border-b border-gray-600">
                                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                    {get_security_badge_color(security)}">
                                        {security}
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap border-b border-gray-600">
                                    <div class="text-sm text-gray-300">{signal_strength}</div>
                                    <div class="w-full bg-gray-600 rounded-full h-2.5">
                                        <div class="{signal_class} h-2.5 rounded-full" style="width: {signal_width}"></div>
                                    </div>
                                </td>
                            </tr>
"""
    
    # Complete the HTML
    html_content += """
                        </tbody>
                    </table>
                </div>
                
                <!-- Chart Section -->
                <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-gray-800 p-4 rounded-lg shadow">
                        <h2 class="text-lg font-semibold mb-4 text-white">Channel Distribution</h2>
                        <canvas id="channelChart" width="400" height="300"></canvas>
                    </div>
                    <div class="bg-gray-800 p-4 rounded-lg shadow">
                        <h2 class="text-lg font-semibold mb-4 text-white">Security Types</h2>
                        <canvas id="securityChart" width="400" height="300"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <script>
        // Network data for JavaScript
        const networkData = {JSON_PLACEHOLDER};
        
        // Sorting function
        function sortTable(column, direction) {
            const table = document.getElementById('networkTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            // Determine column index
            let columnIndex;
            switch(column) {
                case 'ssid': columnIndex = 0; break;
                case 'frequency': columnIndex = 1; break;
                case 'channel': columnIndex = 2; break;
                case 'signal': columnIndex = 3; break;
                case 'security': columnIndex = 4; break;
                default: columnIndex = 0;
            }
            
            // Sort rows
            rows.sort((a, b) => {
                let aValue = a.cells[columnIndex].textContent.trim();
                let bValue = b.cells[columnIndex].textContent.trim();
                
                // Convert to numbers if possible
                if (!isNaN(aValue) && !isNaN(bValue)) {
                    aValue = parseFloat(aValue);
                    bValue = parseFloat(bValue);
                }
                
                if (direction === 'asc') {
                    return aValue > bValue ? 1 : -1;
                } else {
                    return aValue < bValue ? 1 : -1;
                }
            });
            
            // Remove existing rows
            while (tbody.firstChild) {
                tbody.removeChild(tbody.firstChild);
            }
            
            // Add sorted rows
            rows.forEach(row => tbody.appendChild(row));
        }
        
        // Create charts when page loads
        document.addEventListener('DOMContentLoaded', function() {
            Chart.defaults.color = '#f0f0f0';
            Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
            
            // Channel distribution data calculation
            const channelCounts = {};
            networkData.forEach(network => {
                const channel = network.channel;
                if (channel !== "Unknown") {
                    // Handle both numeric and string channels (in case of approx channels like "~6")
                    const cleanChannel = channel.toString().replace(/[^0-9]/g, '');
                    if (cleanChannel) {
                        channelCounts[cleanChannel] = (channelCounts[cleanChannel] || 0) + 1;
                    }
                }
            });
            
            // Sort channels numerically
            const channelLabels = Object.keys(channelCounts).sort((a, b) => parseInt(a) - parseInt(b));
            const channelData = channelLabels.map(channel => channelCounts[channel]);
            
            // Create channel color scheme based on frequency bands
            const channelColors = channelLabels.map(channel => {
                const ch = parseInt(channel);
                if (ch <= 14) {
                    // 2.4 GHz channels (1-14) - blue
                    return 'rgba(59, 130, 246, 0.7)';
                } else if (ch <= 48) {
                    // 5 GHz lower channels - green
                    return 'rgba(16, 185, 129, 0.7)';
                } else if (ch <= 64) {
                    // 5 GHz mid channels - purple
                    return 'rgba(139, 92, 246, 0.7)';
                } else if (ch <= 144) {
                    // 5 GHz upper channels - orange
                    return 'rgba(249, 115, 22, 0.7)';
                } else {
                    // 5 GHz highest channels - red
                    return 'rgba(239, 68, 68, 0.7)';
                }
            });
            
            // Channel Chart at the top
            new Chart(document.getElementById('topChannelChart'), {
                type: 'bar',
                data: {
                    labels: channelLabels,
                    datasets: [{
                        label: 'Networks per Channel',
                        data: channelData,
                        backgroundColor: channelColors,
                        borderColor: channelColors.map(c => c.replace('0.7', '1')),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            },
                            title: {
                                display: true,
                                text: 'Number of Networks',
                                color: '#f0f0f0'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Channel',
                                color: '#f0f0f0'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                title: function(tooltipItems) {
                                    const channel = tooltipItems[0].label;
                                    let band = '';
                                    if (parseInt(channel) <= 14) {
                                        band = '2.4 GHz';
                                    } else {
                                        band = '5 GHz';
                                    }
                                    return `Channel ${channel} (${band})`;
                                }
                            }
                        }
                    }
                }
            });
            
            // Standard Channel Chart (can keep or remove this one)
            new Chart(document.getElementById('channelChart'), {
                type: 'bar',
                data: {
                    labels: channelLabels,
                    datasets: [{
                        label: 'Networks per Channel',
                        data: channelData,
                        backgroundColor: channelColors,
                        borderColor: 'rgba(59, 130, 246, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
            
            // Security types chart
            const securityCounts = {};
            networkData.forEach(network => {
                const security = network.security;
                securityCounts[security] = (securityCounts[security] || 0) + 1;
            });
            
            const securityLabels = Object.keys(securityCounts);
            const securityData = securityLabels.map(security => securityCounts[security]);
            const backgroundColors = [
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 99, 132, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)',
                'rgba(255, 159, 64, 0.6)'
            ];
            
            new Chart(document.getElementById('securityChart'), {
                type: 'pie',
                data: {
                    labels: securityLabels,
                    datasets: [{
                        data: securityData,
                        backgroundColor: backgroundColors.slice(0, securityLabels.length),
                        borderWidth: 1
                    }]
                },
                options: {
                    plugins: {
                        legend: {
                            position: 'right'
                        }
                    }
                }
            });
        });
    </script>
</body>
</html>
""".replace("{timestamp}", timestamp)

    # Replace the JSON placeholder with actual network data
    json_data = json.dumps(networks)
    html_content = html_content.replace("{JSON_PLACEHOLDER}", json_data)
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"{Fore.GREEN}HTML report generated: {os.path.abspath(filename)}{Style.RESET_ALL}")
    
    # Try to open the report in the default browser
    try:
        webbrowser.open('file://' + os.path.abspath(filename))
        print(f"{Fore.CYAN}Opening report in browser...{Style.RESET_ALL}")
    except:
        print(f"{Fore.YELLOW}Unable to open browser automatically. Please open the HTML file manually.{Style.RESET_ALL}")

def check_requirements():
    """Provide OS-specific guidance."""
    os_name = platform.system()
    if os_name == "Windows":
        print(f"{Fore.YELLOW}Note: On Windows, enable Location Services (Settings > Privacy > Location).{Style.RESET_ALL}")
        print("Run as Administrator if issues persist.")
    elif os_name == "Darwin":  # macOS
        print(f"{Fore.YELLOW}Note: On macOS, you may need to run with 'sudo' for Wi-Fi access.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Unsupported OS: {os_name}. This script supports Windows and macOS.{Style.RESET_ALL}")
        sys.exit(1)

def print_network_details(network):
    print(f"\n{Fore.YELLOW}=== NETWORK DEBUG INFO ==={Style.RESET_ALL}")
    print(f"SSID: {network.ssid if network.ssid else '<Hidden>'}")
    print(f"Raw frequency value: {network.freq}")
    print(f"Signal strength: {network.signal}")
    print(f"Network object type: {type(network)}")
    print(f"Network object attributes: {dir(network)}")
    print(f"{Fore.YELLOW}========================={Style.RESET_ALL}\n")

def main():
    """Main entry point for the script."""
    check_requirements()
    try:
        network_data = scan_wifi()
        if network_data:
            generate_html_report(network_data)
    except KeyboardInterrupt:
        print(f"{Fore.YELLOW}Scan interrupted by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()