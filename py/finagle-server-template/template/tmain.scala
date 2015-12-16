package %(groupId)s.%(artifactId)s

import com.twitter.ostrich.admin.{RuntimeEnvironment, Service => OstrichService}
import com.twitter.finagle.builder.{ServerBuilder, Server}
import com.twitter.finagle.http.Http
import com.twitter.finagle.Service
import com.twitter.util.Future
import java.net.InetSocketAddress
import com.twitter.finagle.stats.OstrichStatsReceiver
import com.twitter.ostrich.admin.config.ServerConfig
import org.apache.log4j.{Level, Logger}
import org.slf4j.LoggerFactory
import org.jboss.netty.handler.codec.http._
import org.jboss.netty.buffer.ChannelBuffers

class %(mainClass)sConfig extends ServerConfig[%(mainClass)sServer] {
  var serverPort = 8000
  var log4jLevel = Level.DEBUG

  def apply(runtime: RuntimeEnvironment): %(mainClass)sServer = {
    Logger.getRootLogger.setLevel(log4jLevel)
    new %(mainClass)sServer(this);
  }
}

class %(mainClass)sServer(config:%(mainClass)sConfig) extends OstrichService {
  var server: Server = _
  val log = LoggerFactory.getLogger(getClass)

  // TODO(dirlt): your service.
  val service : Service[HttpRequest, HttpResponse] = new Service[HttpRequest, HttpResponse] {
    def apply(request: HttpRequest): Future[HttpResponse] = {
      val response = new DefaultHttpResponse(HttpVersion.HTTP_1_1, HttpResponseStatus.OK)
      response.setContent(ChannelBuffers.copiedBuffer("OK".getBytes))
      Future(response)
    }
  }

  def start() {
    log.debug("start service...")
    server = ServerBuilder()
      .codec(Http())
      .bindTo(new InetSocketAddress(config.serverPort))
      .reportTo(new OstrichStatsReceiver())
      .name("%(mainClass)s")
      .build(service)
  }

  def shutdown() {
    log.debug("shutdown service...")
    server.close()
  }
}

object %(mainClass)sServer {
  def main(args: Array[String]) {
    val runtime = RuntimeEnvironment(this, args);
    val server = runtime.loadRuntimeConfig[%(mainClass)sServer]()
    server.start()
  }
}
