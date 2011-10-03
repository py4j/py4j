package py4j;

import py4j.commands.Command;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;

/**
 * Builder servide for GatewayServer instances.
 * Created by: Jacek Bzdak
 */
public class GatewayServerBuilder {

   private int port = GatewayServer.DEFAULT_PORT;

	private int pythonPort = GatewayServer.DEFAULT_PYTHON_PORT;

	private InetAddress pythonAddress;

   private InetAddress address;

	private int connectTimeout = GatewayServer.DEFAULT_CONNECT_TIMEOUT;

	private int readTimeout = GatewayServer.DEFAULT_READ_TIMEOUT;

   private final List<Class<? extends Command>> customCommands = new ArrayList<Class<? extends Command>>();

   public GatewayServerBuilder() {
   }

   public GatewayServer buildGatewayServer(Object entryPoint){
      try {
         if(pythonAddress == null){
            pythonAddress =  InetAddress.getLocalHost();
         }
         if(address == null){
            address = InetAddress.getLocalHost();
         }
      } catch (UnknownHostException e) {
         throw new Py4JNetworkException(e);
      }
      return new GatewayServer(entryPoint, port, pythonPort, address, pythonAddress, connectTimeout, readTimeout, customCommands);

   }

   public int getPort() {
      return port;
   }

   public void setPort(int port) {
      this.port = port;
   }

   public int getPythonPort() {
      return pythonPort;
   }

   public void setPythonPort(int pythonPort) {
      this.pythonPort = pythonPort;
   }

   public InetAddress getPythonAddress() {
      return pythonAddress;
   }

   public void setPythonAddress(InetAddress pythonAddress) {
      this.pythonAddress = pythonAddress;
   }

   public InetAddress getAddress() {
      return address;
   }

   public void setAddress(InetAddress address) {
      this.address = address;
   }

   public int getConnectTimeout() {
      return connectTimeout;
   }

   public void setConnectTimeout(int connectTimeout) {
      this.connectTimeout = connectTimeout;
   }

   public int getReadTimeout() {
      return readTimeout;
   }

   public void setReadTimeout(int readTimeout) {
      this.readTimeout = readTimeout;
   }

   public List<Class<? extends Command>> getCustomCommands() {
      return customCommands;
   }


   public boolean addCommand(Class<? extends Command> aClass) {
      return customCommands.add(aClass);
   }

   public boolean addCommand(Class<? extends Command>... aClass) {
      return customCommands.addAll(Arrays.asList(aClass));
   }

   public boolean addCommands(Collection<? extends Class<? extends Command>> c) {
      return customCommands.addAll(c);
   }
}
