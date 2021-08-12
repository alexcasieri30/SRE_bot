from srelib.tsdb.visualization import TSDBGraph
#used for example program in main method
from srelib.metrics.client import MetricRequest, MetricQuery

class MetricGraph(object):
    """Used to create URLs that are used to visualize 
    one or more queries.
    """
    
    def __init__(self):
        pass
        
    @staticmethod
    def get_url_for_metric_request(metric_request_obj, one_graph_tag_list=None):
        """ Obtain the url for the queries in the MetricRequest object.
        Args:
            metric_request_obj (MetricRequest): The MetricRequest object that contains
            one or more queries.
            one_graph_tag_list(List(String)): A list of Tag names that should have their
            values "or" ed together.  For example, including "server_id" in this list
            would cause all the server_ids to be configured in one configuration instead
            of having multiple configurations.
        Returns:
            string: URL string.
        """
        return TSDBGraph.get_url_for_tsdb_request(metric_request_obj, one_graph_tag_list)
        
    @staticmethod
    def get_url_for_metric_tag(start_time, end_time, metric, tags, is_rate, drop_resets=False):
        """ Obtain the url for the parameters passed in.
        Args:
            start_time (str): Start time in this format 2018/09/12-10:58:00
            end_time (str): End time in this format 2018/09/12-10:58:00
            metric (str): The metric
            tags (dictionary): Dicitonary containing tag-values.
            is_rate (bool): True if rates should be graphed. False if counts should be graphed.
        Returns:
            string: URL string.
        """
        #tsdb_graph = TSDBGraph("2018/09/12-10:58:00","2018/09/12-11:08:49")
        tsdb_graph = TSDBGraph(start_time, end_time)
        tsdb_graph.add_query(metric, tags, is_rate, drop_resets)
        url = tsdb_graph.get_url()
        return url
        
def main():
    
    #Alex,Billy use this after checked in.
    url = MetricGraph.get_url_for_metric_tag(
        "2021/06/14-13:00:00",
        "2021/06/14-20:00:00",
        "dma.requests",
        {
            "server_id":"1754",
            "request_type":"RTBMSG",
            "response_code":"SUCCESS"
        },
        True,
        True
    )
    print(url)

    return 0
    #create request with timerange
    metric_request = MetricRequest(1623319308,1623339308)
    #create query object.  Will be used again when obtaining results.
    metric_query_rate = MetricQuery("dma.requests", 
        {
            "server_id":"4719",
            "request_type":"RTBMSG",
            "response_code":"SUCCESS"
        },
        True
    )
    #Add query to request.
    metric_request.add_query(metric_query_rate)
    #Create a second query
    metric_query_rate_2 = MetricQuery("dma.requests", 
        {
            "server_id":"4723",
            "request_type":"RTBMSG",
            "response_code":"SUCCESS"
        },
        True
    )
    metric_request.add_query(metric_query_rate_2)
    graph_url = MetricGraph.get_url_for_metric_request(metric_request)
    print(graph_url)

    #agg_list = ["server_id"]
    #graph_url = MetricGraph.get_url_for_metric_request(metric_request, agg_list)
    #print(graph_url)
    
        
if __name__ == '__main__':
    main()