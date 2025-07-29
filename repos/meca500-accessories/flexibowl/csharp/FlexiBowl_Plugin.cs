using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net;
using System.Net.Sockets;
using System.IO;

namespace Mecademic_Plugin
{
    /// <summary>
    /// FlexiBowl Plugin for Mecademic robots
    /// Provides UDP communication with FlexiBowl feeder systems
    /// </summary>
    class Flexibowl_Plugin
    {
        UdpClient m_udpClient = new UdpClient(7777);
        TcpClient m_tcpClient;
        NetworkStream m_tcpStream;
        bool m_useTcp = false;
        
        // Command mapping dictionary
        private static readonly Dictionary<string, string> CommandMap = new Dictionary<string, string>
        {
            {"MOVE", "QX2"},
            {"MOVE FLIP", "QX3"},
            {"MOVE BLOW FLIP", "QX4"},
            {"MOVE BLOW", "QX5"},
            {"SHAKE", "QX6"},
            {"LIGHT ON", "QX7"},
            {"LIGHT OFF", "QX8"},
            {"FLIP", "QX10"},
            {"BLOW", "QX9"},
            {"QUICK EMPTY OPTION", "QX11"}
        };

        /// <summary>
        /// Constructor - defaults to UDP communication
        /// </summary>
        public Flexibowl_Plugin() : this(false) { }
        
        /// <summary>
        /// Constructor with protocol selection
        /// </summary>
        /// <param name="useTcp">True for TCP connection (port 7776), False for UDP (port 7775)</param>
        public Flexibowl_Plugin(bool useTcp)
        {
            m_useTcp = useTcp;
            if (useTcp)
            {
                m_tcpClient = new TcpClient();
                m_tcpClient.ReceiveTimeout = 2000;
                m_tcpClient.SendTimeout = 2000;
            }
        }

        /// <summary>
        /// Check FlexiBowl alarm status
        /// </summary>
        /// <param name="ipAddress">FlexiBowl IP address</param>
        /// <returns>True if no alarm, False if in alarm state</returns>
        public bool CheckAlarmStatus(string ipAddress)
        {
            try
            {
                string response = SendTcpCommand(ipAddress, "AL");
                if (string.IsNullOrEmpty(response) || response.Length < 8)
                    return false;

                // Extract hex data starting from position 5 (like Python my_hexdata = data[5:None])
                string hexData = response.Substring(5).Trim('\r', '\n', '\0');
                
                // Convert hex to binary and check for errors
                if (int.TryParse(hexData, System.Globalization.NumberStyles.HexNumber, null, out int hexValue))
                {
                    // Convert to 16-bit binary
                    string binary = Convert.ToString(hexValue, 2).PadLeft(16, '0');
                    int errorDecimal = Convert.ToInt32(binary, 2);
                    return errorDecimal == 0; // False if error (>0), True if no error (0)
                }
                return false;
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Send command using friendly name (e.g., "MOVE", "LIGHT ON")
        /// </summary>
        /// <param name="ipAddress">FlexiBowl IP address</param>
        /// <param name="friendlyCommand">Friendly command name</param>
        /// <returns>Response string or error message</returns>
        public string FlexibowlFriendly(string ipAddress, string friendlyCommand)
        {
            string sclCommand = CommandMap.ContainsKey(friendlyCommand.ToUpper()) 
                ? CommandMap[friendlyCommand.ToUpper()] 
                : "QX60"; // Invalid command
            
            return m_useTcp ? SendTcpCommand(ipAddress, sclCommand) : Flexibowl(ipAddress, sclCommand);
        }

        /// <summary>
        /// Send command to FlexiBowl and receive response
        /// </summary>
        /// <param name="ipAddress">FlexiBowl IP address (e.g., "192.168.0.130")</param>
        /// <param name="command">SCL command (e.g., "QX2", "AL")</param>
        /// <returns>Response string or error message</returns>
        public string Flexibowl(string ipAddress, string command)
        {
            string m_IpAddress = ipAddress;
            string m_command = command;
            string receiveString = "";
            string ReturnFlexibowl = "";
            int byteSent = 0;

            IPEndPoint ep = new IPEndPoint(0, 0);
            try
            {
                ep = new IPEndPoint(IPAddress.Parse(m_IpAddress), 7775);
                m_udpClient.Connect(ep);
                m_udpClient.Client.SendTimeout = 500;
                m_udpClient.Client.ReceiveTimeout = 500;
            }
            catch (Exception ex)
            {
                ReturnFlexibowl = ex.ToString();
                return ReturnFlexibowl;
            }

            string dataToSend = m_command.ToUpper();
            try
            {
                // Create SCL packet: header + command + terminator
                Byte[] SCLstring = Encoding.ASCII.GetBytes(dataToSend);
                Byte[] sendBytes = new Byte[SCLstring.Length + 3];
                sendBytes[0] = 0;  // Header byte 1
                sendBytes[1] = 7;  // Header byte 2
                System.Array.Copy(SCLstring, 0, sendBytes, 2, SCLstring.Length);
                sendBytes[sendBytes.Length - 1] = 13; // CR terminator
                
                byteSent = m_udpClient.Send(sendBytes, sendBytes.Length);
                var receivedData = m_udpClient.Receive(ref ep);
                receiveString = Encoding.ASCII.GetString(receivedData);

                // Handle movement commands that return "%" (motion in progress)
                if ((receiveString.Contains("%")) && (dataToSend.Contains("Q")))
                {
                    bool moving = true;
                    while (moving == true)
                    {
                        string statusCommand;
                        // Use different status commands based on the operation (matching Python logic)
                        if (dataToSend == "QX11" || dataToSend == "QX10" || dataToSend == "QX4" || dataToSend == "QX3")
                        {
                            statusCommand = "IO";
                        }
                        else
                        {
                            statusCommand = "SC";
                        }
                        
                        SCLstring = Encoding.ASCII.GetBytes(statusCommand);
                        sendBytes = new Byte[SCLstring.Length + 3];
                        sendBytes[0] = 0;
                        sendBytes[1] = 7;
                        System.Array.Copy(SCLstring, 0, sendBytes, 2, SCLstring.Length);
                        sendBytes[sendBytes.Length - 1] = 13; // CR
                        
                        byteSent = m_udpClient.Send(sendBytes, sendBytes.Length);
                        receivedData = m_udpClient.Receive(ref ep);
                        receiveString = Encoding.ASCII.GetString(receivedData);
                        
                        // Parse status based on command type (matching Python logic)
                        if (statusCommand == "IO")
                        {
                            // For IO command, check data[12:-1] == 1 to break (Python logic)
                            if (receivedData.Length > 13)
                            {
                                string movingStatus = Encoding.ASCII.GetString(receivedData, 12, receivedData.Length - 13);
                                if (int.TryParse(movingStatus, out int status) && status == 1)
                                {
                                    moving = false;
                                }
                            }
                        }
                        else
                        {
                            // For SC command, check data[7:-2] == 0 to break (Python logic)
                            if (receivedData.Length > 9)
                            {
                                string movingStatus = Encoding.ASCII.GetString(receivedData, 7, receivedData.Length - 9);
                                if (int.TryParse(movingStatus, out int status) && status == 0)
                                {
                                    moving = false;
                                }
                            }
                        }
                        
                        System.Threading.Thread.Sleep(100);
                    }
                    System.Threading.Thread.Sleep(100);
                    ReturnFlexibowl = "Done";
                    return ReturnFlexibowl;
                }
                else
                {
                    // Extract response without header
                    SCLstring = new Byte[receivedData.Length - 3];
                    System.Array.Copy(receivedData, 2, SCLstring, 0, SCLstring.Length);
                    receiveString = Encoding.ASCII.GetString(SCLstring);
                    ReturnFlexibowl = receiveString;
                }
                return ReturnFlexibowl;
            }
            catch (Exception ex)
            {
                ReturnFlexibowl = ex.ToString();
                return ReturnFlexibowl;
            }
        }

        /// <summary>
        /// Send TCP command to FlexiBowl
        /// </summary>
        /// <param name="ipAddress">FlexiBowl IP address</param>
        /// <param name="command">SCL command</param>
        /// <returns>Response string</returns>
        private string SendTcpCommand(string ipAddress, string command)
        {
            try
            {
                if (!m_tcpClient.Connected)
                {
                    m_tcpClient.Connect(ipAddress, 7776);
                    m_tcpStream = m_tcpClient.GetStream();
                }

                // Create SCL packet: header + command + terminator
                byte[] commandBytes = Encoding.ASCII.GetBytes(command.ToUpper());
                byte[] message = new byte[commandBytes.Length + 3];
                message[0] = 0;  // Header byte 1
                message[1] = 7;  // Header byte 2
                Array.Copy(commandBytes, 0, message, 2, commandBytes.Length);
                message[message.Length - 1] = 13; // CR terminator

                m_tcpStream.Write(message, 0, message.Length);
                
                // Read response
                byte[] buffer = new byte[1024];
                int bytesRead = m_tcpStream.Read(buffer, 0, buffer.Length);
                
                if (bytesRead > 0)
                {
                    return Encoding.ASCII.GetString(buffer, 0, bytesRead);
                }
                return "";
            }
            catch (Exception ex)
            {
                return ex.ToString();
            }
        }

        /// <summary>
        /// Close connections and dispose resources
        /// </summary>
        public void Flexibowl_Close()
        {
            if (m_useTcp)
            {
                m_tcpStream?.Close();
                m_tcpClient?.Close();
            }
            else
            {
                m_udpClient?.Dispose();
            }
        }
    }

    /// <summary>
    /// Example usage of FlexiBowl Plugin
    /// </summary>
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("///////////FLEXIBOWL PLUGIN EXAMPLE MECADEMIC/////////////");
            string returnFlbString = "";
            
            // Example using TCP connection (like Python version)
            Flexibowl_Plugin Fb = new Flexibowl_Plugin(true);
            
            // Also demonstrate UDP version
            // Flexibowl_Plugin Fb = new Flexibowl_Plugin(false);
            
            // Check alarm status using dedicated method
            bool alarmStatus = Fb.CheckAlarmStatus("192.168.0.161");
            Console.WriteLine($"Alarm Status: {(alarmStatus ? "OK" : "ALARM")}");
            
            // Execute move command using friendly names
            returnFlbString = Fb.FlexibowlFriendly("192.168.0.161", "MOVE");
            Console.WriteLine($"Move Result: {returnFlbString}");
            
            // Execute move with flip using friendly name
            returnFlbString = Fb.FlexibowlFriendly("192.168.0.161", "MOVE FLIP");
            Console.WriteLine($"Move-Flip Result: {returnFlbString}");
            
            // Execute light control
            returnFlbString = Fb.FlexibowlFriendly("192.168.0.161", "LIGHT ON");
            Console.WriteLine($"Light On Result: {returnFlbString}");
            
            System.Threading.Thread.Sleep(1000);
            
            returnFlbString = Fb.FlexibowlFriendly("192.168.0.161", "LIGHT OFF");
            Console.WriteLine($"Light Off Result: {returnFlbString}");
            
            // Close connection
            Fb.Flexibowl_Close();
            Console.ReadLine();
        }
    }
}