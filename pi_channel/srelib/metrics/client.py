import copy
import logging
from srelib.tsdb.client import TSDBClient,TSDBRequest,TSDBQuery, QueryRateOptions
#from metrics.visualization import MetricGraph

class MetricClient(object):
    """ Used to execute a time seried data request.

        This is used as an abstraction layer to shield the backend.

        This implementation code will have to change in order to switch a backend
        but hopefully the client code calling this layer can remain the same.
    """
    logger = logging.getLogger(__name__)
    def __init__(self):
        pass
    
    def execute_request(self, metric_request_obj):
        """ Executes the request.
        
        Args:
            metric_request_obj (MetricRequest):  The request object containing the queries that
            will be executed.
        Returns:
            MetricRequestResponse: The response object that contains one or more results.
        """
        client = TSDBClient()
        self.logger.debug("Executing query request.")
        tsdb_obj_list = client.execute_request(metric_request_obj._get_tsdb_request_obj())
        self.logger.debug("Query request completed.")
        return MetricRequestResponse(tsdb_obj_list)
    
class MetricRequest(object):
    """ This is used as an abstraction layer to shield the backend from the client. A request object
    is used to configure one or more queries to perform on the backend.

    This implementation code will have to change in order to switch a backend. 

    If possible, all queries in one MetricRequest object
    will be executed in one request to the backend.

    All queries added to the MetricRequest object will be executed for the
    timespan specified in the constructor.
    """

    def __init__(self, start_time, end_time):
        """
        Args:
            start_time(int):  Start time in seconds after epoch.
            end_time(int): End time in seconds after epoch.
        """
        self.start_time = start_time
        self.end_time = end_time
        self.request = TSDBRequest()
        self.request.set_start_time(start_time)
        self.request.set_end_time(end_time)
        
    def get_start_time(self):
        """
        Returns:
            int: The start time for the query.  In seconds since epoch.
        """
        return self.request.get_start_time()
        
    def get_end_time(self):
        """
        Returns:
            int: The ed time for the query.  In seconds since epoch.
        """
        return self.request.get_end_time()
    
    def add_query(self, metric_query_obj):
        """ Adds a metric query to this request object.
        Args:
            metric_query_obj (MetricQuery): The query object object.
        Returns:
            None
        """
        metric = metric_query_obj.get_metric()
        tag_dictionary = metric_query_obj.get_tag_dictionary()
        is_rate = metric_query_obj.get_is_rate()
        tsdb_query_obj = self._add_query(metric, tag_dictionary, is_rate)
        metric_query_obj._set_tsdb_query_obj(tsdb_query_obj)
        
    def get_queries(self):
        """ Returns instances of the implementation classes used
        to configure the queries in this request.
        Returns:
            List(Objects):  Objects that implement a Query interface.
        """
        return self.request.get_queries()
        
             
    def _add_query(self, metric, tag_dictionary, is_rate):
        query = TSDBQuery()
        query.set_metric(metric)
        for key,val in tag_dictionary.items():
            query.add_tag_value(key,val)
        if(is_rate == True):
            qra = QueryRateOptions()
            qra.set_is_drop_resets(True)
            #query.set_rate_options(qra)
            pass
        else:
            query.set_is_rate(False)
        self.request.add_query(query)
        return query
        
    
        
    def _get_tsdb_request_obj(self):
        """ This is not a method in the interface. """
        return self.request
        
    def __str__(self):
        return "Metric Request\nStart:{}\nEnd:{}".format(
            self.get_start_time(),
            self.get_end_time()
        )
            
    def __repr__(self):
        return self.__str__()

class MetricRequestResponse(object):
    """ This is used to hold the results of a request.
    """
    
    def __init__(self, list_tsdb_objs):
        """
        Args:
            list_tsdb_objs (List): Contains a list of QueryResponses objects.
        """
        self.list_tsdb_objs = list_tsdb_objs
        
    def get_query_result(self, metric_query_obj):
        """ Returns a MetricQueryResponse object for the given MetricQuery object.
        
        Interface method.
        Args:
            metric_query_obj (MetricQuery): The metric query object that caller wants
            results.
        Returns:
            MetricQueryResponse: A query response object for the given MetricQuery.
            None if backend didn't return anything for the given MetricQuery or invalid
            MetricQuery.
        """
        query_key = metric_query_obj.get_key_representation_dict()
        for parent_result_obj in self.list_tsdb_objs:
            parent_key = parent_result_obj.get_key_representation_dict()
            if(parent_key == query_key):
                return MetricQueryResponse(parent_result_obj)
                
        return None
           
class MetricQuery(object):
    """Used to configure a metric query.  This is then added to a 
    MetricRequest.
    
    """
    def __init__(self, metric, tag_dictionary, is_rate):
        """  Configures the query with the given metric, 
            tag_dictionary and is_rate.
        
        Args:
            metric (str): The metric.
            tag_dictionary (dictionary): Dictionary containing tag-values.
            is_rate (bool):  If set to true then the returned datapoints
            will be rates.  If false then the data points will be 
            counts.
        """
        self.metric = metric
        self.tag_dictionary = tag_dictionary
        self.is_rate = is_rate
        
    def get_is_rate(self):
        """
        Returns: 
            Boolean: True if the query is for rate data.  False if 
            query is for count data.
        """
        return self.is_rate
        
    def get_metric(self):
        """
        Returns:
            String: The metric
        """
        return self.metric
        
    def get_tag_dictionary(self):
        """
        Returns:
            Dictionary:  Key is the tag name, Value is the value for the tag.
        """
        my_copy = copy.deepcopy(self.tag_dictionary)
        return my_copy
        
    def get_key_representation_dict(self):
        """
        Returns:
            Dictionary: This object represented as a dictionary.
        """
        return {
            "metric":self.metric,
            "tags":self.tag_dictionary,
            "rate":self.is_rate
        }
        
    def _set_tsdb_query_obj(self, tsdb_query_obj):
        """ Internal method to bookkeep the tsdb query object.
        Args:
            tsdb_query_obj(TSDBQuery): tsdb query object.
        Returns:
            None
        """
        self.tsdb_query = tsdb_query_obj
    
    def _get_tsdb_query_obj(self):
        """
        Returns:
            TSDBQuery: The internal tsdb query object.
        """
        return self.tsdb_query
        
class MetricQueryResponse(object):
    """ This is used to hold the results of the metric query.
        
    """
    
    def __init__(self, query_result_tsdb_obj):
        """
        Args:
            query_result_tsdb_obj: The parent object returned by the tsdb query.  This contains
            the actual query results for the given query.
        """
        self.query_result_tsdb_obj = query_result_tsdb_obj
        
    def get_time_series_data_dict(self, metric, tag_dictionary, is_rate):
        """ Returns the timeseries data in dictionary form.  
        This is used when the query returns multiple time series data 
        results due to an "or" operator in a tag value.
        Returns:
            dictionary: Dictionary where the key is the timestamp and the value is what
            the backend calculated.
            None is returned if metric-tag-values are not found.
        """
        test_dict = {
            "metric":metric,
            "tags":tag_dictionary,
            "rate":is_rate
        }
        for query_result in self.query_result_tsdb_obj.get_query_results():
            query_key_rep = query_result.get_key_representation_dict()
            if(query_key_rep == test_dict):
                return query_result.get_time_series_data_dict()
        return None        
    
    def get_all_results(self):
        """ Returns a list of objects that implements the QueryResponse interface"""
        return self.query_result_tsdb_obj.get_query_results()
             
def main():

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
    
    #Create a query that requests counts instead of rate.
    metric_query_count = MetricQuery("dma.requests", 
        {
            "server_id":"4723",
            "request_type":"RTBMSG",
            "response_code":"SUCCESS"
        },
        False
    )
    metric_request.add_query(metric_query_count)
    
    #Issue request to the metric client.
    client = MetricClient()
    metric_resp_obj = client.execute_request(metric_request)
    
    #Ask the response object for the results of the metric query.
    rate_results = metric_resp_obj.get_query_result(metric_query_rate)
    
    #asking for a specific metric with tag-name tag-values.
    #data_dict = rate_results.get_time_series_data_dict("bsy.messaging.results",{"server_id":"4518", "status_code":"STATUS_BLOCKED_DOMAIN"}, True)
    #print(data_dict)
    
    #ask for all the metric query results 
    result_list = rate_results.get_all_results()
    
    #iterate through all the rate results and print out inforamtion about each rate result.
    for result in result_list:
        print("\nMetric={}\nTags={}\ndata_points={}\n".format(result.get_metric(), result.get_tag_dictionary(), result.get_time_series_data_dict()))
    
    #print out result for count query
    result_list =  metric_resp_obj.get_query_result(metric_query_count).get_all_results()
    for result in result_list:
        print("\nMetric={}\nTags={}\ndata_points={}\n".format(result.get_metric(), result.get_tag_dictionary(), result.get_time_series_data_dict()))
    
    return 0
    
    #includes all the queries in the request on one graph
    #url = MetricGraph.get_url_for_metric_request(metric_request)
    #print(url)
    
    #includes a list of MetricQueries on one graph
    #query_list = [metric_query_count]
    #url = MetricGraph.get_url_for_metric_queries(metric_request, query_list)
    #print(url)
    
    
    #Now get information for the count instead of rate.
    count_results = metric_resp_obj.get_query_result(metric_query_count)
    data_dict = count_results.get_time_series_data_dict("bsy.messaging.results",{"server_id":"4518", "status_code":"STATUS_BLOCKED_DOMAIN"},False)
    print(data_dict)
    
    #ask for all the metric query results 
    result_list = count_results.get_all_results()
    
    #iterate through all the rate results and print out inforamtion about each rate result.
    for result in result_list:
        print("\nMetric={}\nTags={}\ndata_points={}\n".format(result.get_metric(), result.get_tag_dictionary(), result.get_time_series_data_dict()))
      
if __name__ == '__main__':
    main()