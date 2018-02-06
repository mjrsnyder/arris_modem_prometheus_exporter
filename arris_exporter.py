from prometheus_client import start_http_server, Metric, REGISTRY
import sys
import time
import os
import pandas

class JsonCollector(object):
  def __init__(self, host):
    self._host = host
  def collect(self):
    
    try:
      tables = pandas.read_html(io="http://" + self._host + "/cgi-bin/status_cgi", header=0)
      downstreams = tables[1]
      upstreams = tables[3]

      # Downstreams
      metric = Metric('arris_downstream_channel_gauges', 'Power of each channel', 'gauge')
      for channel in downstreams.itertuples(index=True, name='Pandas'):
        power = float(getattr(channel, "Power").split(' ')[0])
        snr = float(getattr(channel, "SNR").split(' ')[0])
        frequency = float(getattr(channel, "Freq").split(' ')[0])
        
        d_channel_id = str(getattr(channel, "DCID"))

        metric.add_sample('arris_downstream_channel_snr',
          value=snr,
          labels={'DCID' : d_channel_id})
        metric.add_sample('arris_downstream_channel_power',
          value=power,
          labels={'DCID' : d_channel_id})
        metric.add_sample('arris_downstream_channel_frequency',
          value=frequency,
          labels={'DCID' : d_channel_id})
      yield metric

      metric = Metric('arris_downstream_channel_counters', 'Counters for each channel', 'counter')
      for channel in downstreams.itertuples(index=True, name='Pandas'):
        octets = int(getattr(channel, "Octets"))
        correcteds = int(getattr(channel, "Correcteds"))
        uncorrectables = int(getattr(channel, "Uncorrectables"))
        d_channel_id = str(getattr(channel, "DCID"))

        metric.add_sample('arris_downstream_channel_octets',
          value=octets,
          labels={'DCID' : d_channel_id})
        metric.add_sample('arris_downstream_channel_correcteds',
          value=correcteds,
          labels={'DCID' : d_channel_id})
        metric.add_sample('arris_downstream_channel_uncorrectables',
          value=uncorrectables,
          labels={'DCID' : d_channel_id})
      yield metric

    except:
      print('Failed to collect data')

if __name__ == '__main__':

  # Get config options via env vars
  host = os.environ.get('ARRIS_IP', '192.168.100.1')

  interval = os.environ.get('EXPORTER_INTERVAL', 5)
  port = os.environ.get('EXPORTER_PORT', 6133)

  # Usage: json_exporter.py port endpoint
  start_http_server(int(port))
  REGISTRY.register(JsonCollector(host))

  while True: time.sleep(interval)

