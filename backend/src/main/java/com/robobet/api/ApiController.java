package com.robobet.api;
import org.springframework.web.bind.annotation.*;import org.springframework.http.*;import java.net.*;import java.net.http.*;import java.time.*;
@RestController @RequestMapping("/api") public class ApiController{
 private ResponseEntity<String> ml(String method,String path,String body){
  try{
   var c=HttpClient.newHttpClient();
   var b=HttpRequest.newBuilder(URI.create("http://ml:8001"+path)).header("Content-Type","application/json");
   HttpRequest r=("POST".equals(method)?b.POST(HttpRequest.BodyPublishers.ofString(body==null?"{}":body)):b.GET()).build();
   var x=c.send(r,HttpResponse.BodyHandlers.ofString());
   return ResponseEntity.status(x.statusCode()).body(x.body());
  }catch(Exception e){
   return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body("{\"status\":\"ml_unavailable\",\"error\":\""+e.getClass().getSimpleName()+"\"}");
  }
 }
 @GetMapping("/health") public Object health(){return java.util.Map.of("status","ok","version","25.0.0","timestamp",Instant.now().toString(),"real_money_execution",false);}
 @GetMapping("/ml/health") public ResponseEntity<String> mlHealth(){return ml("GET","/health",null);}
 @GetMapping("/research/status") public ResponseEntity<String> researchStatus(){return ml("GET","/research/status",null);}
 @GetMapping("/bets") public ResponseEntity<String> bets(){return ml("GET","/bets",null);} @GetMapping("/decisions") public ResponseEntity<String> decisions(){return ml("GET","/decisions",null);}
 @GetMapping("/performance") public ResponseEntity<String> performance(){return ml("GET","/performance",null);} @GetMapping("/risk") public ResponseEntity<String> risk(){return ml("GET","/risk",null);}
 @GetMapping("/research/models") public ResponseEntity<String> models(){return ml("GET","/research/models",null);} @GetMapping("/research/metrics") public ResponseEntity<String> metrics(){return ml("GET","/research/metrics",null);}
 @GetMapping("/research/experiments") public ResponseEntity<String> experiments(){return ml("GET","/research/experiments",null);} @GetMapping("/research/datasets") public ResponseEntity<String> datasets(){return ml("GET","/research/datasets",null);}
 @GetMapping("/research/validation") public ResponseEntity<String> validation(){return ml("GET","/research/validation",null);} @GetMapping("/research/holdout") public ResponseEntity<String> holdout(){return ml("GET","/research/holdout",null);}
 @GetMapping("/research/data-quality") public ResponseEntity<String> dataQuality(){return ml("GET","/research/data-quality",null);} @GetMapping("/calibration") public ResponseEntity<String> calibration(){return ml("GET","/calibration",null);}
 @GetMapping("/drift") public ResponseEntity<String> drift(){return ml("GET","/drift",null);} @GetMapping("/research/ingestion/status") public ResponseEntity<String> ingestionStatus(){return ml("GET","/research/ingestion/status",null);}
 @GetMapping("/v20/status") public ResponseEntity<String> v20Status(){return ml("GET","/v20/status",null);}
 @GetMapping("/v21/status") public ResponseEntity<String> v21Status(){return ml("GET","/v21/status",null);}
 @GetMapping("/v21/ledger") public ResponseEntity<String> v21Ledger(){return ml("GET","/v21/ledger",null);}
 @GetMapping("/v21/performance") public ResponseEntity<String> v21Performance(){return ml("GET","/v21/performance",null);}
 @GetMapping("/v21/research") public ResponseEntity<String> v21Research(){return ml("GET","/v21/research",null);} @GetMapping("/v20/performance") public ResponseEntity<String> v20Performance(){return ml("GET","/v20/performance",null);} @GetMapping("/v20/ledger") public ResponseEntity<String> v20Ledger(){return ml("GET","/v20/ledger",null);} @GetMapping("/v20/notifications") public ResponseEntity<String> v20Notifications(){return ml("GET","/v20/notifications",null);}
 @PostMapping("/v20/select") public ResponseEntity<String> v20Select(@RequestBody String body){return ml("POST","/v20/select",body);} @PostMapping("/v20/live/reprice") public ResponseEntity<String> v20Live(@RequestBody String body){return ml("POST","/v20/live/reprice",body);} @PostMapping("/v20/paper/record") public ResponseEntity<String> v20Paper(@RequestBody String body){return ml("POST","/v20/paper/record",body);} @PostMapping("/v20/ledger/settle") public ResponseEntity<String> v20Settle(@RequestBody String body){return ml("POST","/v20/ledger/settle",body);} @PostMapping("/v20/ledger/export") public ResponseEntity<String> v20Export(@RequestBody(required=false) String body){return ml("POST","/v20/ledger/export",body);}
 @PostMapping("/v21/select") public ResponseEntity<String> v21Select(@RequestBody String body){return ml("POST","/v21/select",body);}
 @PostMapping("/v21/kill-switch") public ResponseEntity<String> v21KillSwitch(@RequestBody String body){return ml("POST","/v21/kill-switch",body);}
 @PostMapping("/v21/ledger/settle") public ResponseEntity<String> v21Settle(@RequestBody String body){return ml("POST","/v21/ledger/settle",body);}
 @PostMapping("/v21/ledger/export") public ResponseEntity<String> v21Export(@RequestBody(required=false) String body){return ml("POST","/v21/ledger/export",body);}
 @GetMapping("/v22/status") public ResponseEntity<String> v22Status(){return ml("GET","/v22/status",null);}
 @GetMapping("/v22/metrics") public ResponseEntity<String> v22Metrics(){return ml("GET","/v22/metrics",null);}
 @GetMapping("/v22/dataset") public ResponseEntity<String> v22Dataset(){return ml("GET","/v22/dataset",null);}
 @PostMapping("/v22/feed/poll") public ResponseEntity<String> v22FeedPoll(){return ml("POST","/v22/feed/poll",null);}
 @GetMapping("/v22/replay/{eventId}") public ResponseEntity<String> v22Replay(@PathVariable String eventId){return ml("GET","/v22/replay/"+eventId,null);}
 @PostMapping("/v22/session/poll") public ResponseEntity<String> v22Session(@RequestParam(defaultValue="SHADOW") String mode){return ml("POST","/v22/session/poll?mode="+mode,null);}
 @PostMapping("/v22/scan") public ResponseEntity<String> v22Scan(@RequestBody(required=false) String body){return ml("POST","/v22/scan",body);}
 @PostMapping("/v22/position/assess") public ResponseEntity<String> v22PositionAssess(@RequestBody String body){return ml("POST","/v22/position/assess",body);}
 @PostMapping("/v22/position/reverse") public ResponseEntity<String> v22PositionReverse(@RequestBody String body){return ml("POST","/v22/position/reverse",body);}


 @GetMapping("/v25/status") public ResponseEntity<String> v25Status(){return ml("GET","/v25/status",null);}
 @GetMapping("/v25/infra/health") public ResponseEntity<String> v25Infra(){return ml("GET","/v25/infra/health",null);}
 @GetMapping("/v25/dataset") public ResponseEntity<String> v25Dataset(){return ml("GET","/v25/dataset",null);}
 @GetMapping("/v25/analytics") public ResponseEntity<String> v25Analytics(){return ml("GET","/v25/analytics",null);} @GetMapping("/v25/observability") public ResponseEntity<String> v25Observability(){return ml("GET","/v25/observability",null);}
 @GetMapping("/v25/hash-chain") public ResponseEntity<String> v25Hash(){return ml("GET","/v25/hash-chain",null);}
 @PostMapping("/v25/feed/poll") public ResponseEntity<String> v25FeedPoll(){return ml("POST","/v25/feed/poll",null);}
 @PostMapping("/v25/session/scan") public ResponseEntity<String> v25Scan(@RequestParam(defaultValue="SHADOW") String mode){return ml("POST","/v25/session/scan?mode="+mode,null);}
 @PostMapping("/v25/market/analyze") public ResponseEntity<String> v25MarketAnalyze(@RequestBody String body){return ml("POST","/v25/market/analyze",body);}
 @PostMapping("/v25/export/xlsx") public ResponseEntity<String> v25Export(){return ml("POST","/v25/export/xlsx",null);}
 @PostMapping("/v25/kill-switch") public ResponseEntity<String> v25Kill(@RequestParam(defaultValue="true") boolean enabled,@RequestParam(defaultValue="MANUAL") String reason){return ml("POST","/v25/kill-switch?enabled="+enabled+"&reason="+reason,null);}
 @PostMapping("/v25/live/reprice") public ResponseEntity<String> v25LiveReprice(@RequestBody String body){return ml("POST","/v25/live/reprice",body);}
 @PostMapping("/v25/live/snapshot") public ResponseEntity<String> v25LiveSnapshot(@RequestBody String body){return ml("POST","/v25/live/snapshot",body);}
 @GetMapping("/v25/live/{eventId}") public ResponseEntity<String> v25Live(@PathVariable String eventId){return ml("GET","/v25/live/"+eventId,null);}
 @PostMapping("/v25/position/reassess") public ResponseEntity<String> v25PositionReassess(@RequestBody String body){return ml("POST","/v25/position/reassess",body);}
 @PostMapping("/v25/position/settle") public ResponseEntity<String> v25PositionSettle(@RequestBody String body){return ml("POST","/v25/position/settle",body);}
 @PostMapping("/v25/position/reversal") public ResponseEntity<String> v25PositionReversal(@RequestBody String body){return ml("POST","/v25/position/reversal",body);}
 @PostMapping("/v25/replay") public ResponseEntity<String> v25Replay(@RequestBody String body){return ml("POST","/v25/replay",body);}
 @PostMapping("/v25/notification/test") public ResponseEntity<String> v25NotificationTest(@RequestBody String body){return ml("POST","/v25/notification/test",body);}
 @PostMapping("/v25/watchlist") public ResponseEntity<String> v25WatchlistAdd(@RequestBody String body){return ml("POST","/v25/watchlist",body);}
 @GetMapping("/v25/watchlist") public ResponseEntity<String> v25Watchlist(){return ml("GET","/v25/watchlist",null);}

 @GetMapping("/v24/status") public ResponseEntity<String> v24Status(){return ml("GET","/v24/status",null);}
 @GetMapping("/v24/dataset") public ResponseEntity<String> v24Dataset(){return ml("GET","/v24/dataset",null);}
 @GetMapping("/v24/analytics") public ResponseEntity<String> v24Analytics(){return ml("GET","/v24/analytics",null);}
 @PostMapping("/v24/export/xlsx") public ResponseEntity<String> v24Export(){return ml("POST","/v24/export/xlsx",null);}
 @GetMapping("/v24/hash-chain") public ResponseEntity<String> v24Hash(){return ml("GET","/v24/hash-chain",null);}
 @PostMapping("/v24/feed/poll") public ResponseEntity<String> v24FeedPoll(){return ml("POST","/v24/feed/poll",null);}
 @PostMapping("/v24/session/scan") public ResponseEntity<String> v24Scan(@RequestParam(defaultValue="SHADOW") String mode){return ml("POST","/v24/session/scan?mode="+mode,null);}
 @PostMapping("/v24/kill-switch") public ResponseEntity<String> v24Kill(@RequestParam(defaultValue="true") boolean enabled,@RequestParam(defaultValue="MANUAL") String reason){return ml("POST","/v24/kill-switch?enabled="+enabled+"&reason="+reason,null);}
 @PostMapping("/v24/live/snapshot") public ResponseEntity<String> v24LiveSnapshot(@RequestBody String body){return ml("POST","/v24/live/snapshot",body);}
 @GetMapping("/v24/live/{eventId}") public ResponseEntity<String> v24Live(@PathVariable String eventId){return ml("GET","/v24/live/"+eventId,null);}
 @PostMapping("/v24/replay/compare") public ResponseEntity<String> v24Replay(@RequestBody String body){return ml("POST","/v24/replay/compare",body);}
}
