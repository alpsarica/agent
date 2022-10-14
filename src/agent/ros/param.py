import json
import rospy
import rosparam

import agent.ros.command as command

import muto_msgs.srv as muto_srv




class RosParamCommands(object):

    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

        self.rosparam_get = rospy.Service(
            "rosparam_get", muto_srv.CommandPlugin, self.handle_param_get)
        self.rosparam_set = rospy.Service(
            "rosparam_set", muto_srv.CommandPlugin, self.handle_param_set)
        self.rosparam_list = rospy.Service(
            "rosparam_list", muto_srv.CommandPlugin, self.handle_param_list)
        self.rosparam_delete = rospy.Service(
            "rosparam_delete", muto_srv.CommandPlugin, self.handle_param_delete)
    


    def handle_param_get(self, req):
        payload = json.loads(req.input.payload)
        requested_key = payload["param"]
        param = {"name": requested_key,
                 "value": "",}
        if rospy.has_param(requested_key):
            param["value"] = rosparam.get_param(requested_key)
        msg = command.to_stdmsgs_string(json.dumps(param))
        return command.to_commandoutput(msg.data)


    def handle_param_set(self, req):
        payload = json.loads(req.input.payload)
        requested_key = payload["param"]
        new_value = payload["value"]
        param = {"name": requested_key,
                 "value": "", "previosValue": ""}
        if rospy.has_param(requested_key):
            # regex should be implemented and prev value - current val should be checked
            param["previosValue"] = rosparam.get_param(requested_key)
            rospy.set_param(requested_key, new_value)
            param["value"] = rosparam.get_param(requested_key)
            msg = command.to_stdmsgs_string(json.dumps(param))
            return command.to_commandoutput(msg.data)
        return command.to_commandoutput(req.input.payload)
        

    def handle_param_list(self, req):
        parameterNames = rospy.get_param_names()
        result = { "params": [] }
        for p in parameterNames:
            result["params"].append({"name": p, "value": rosparam.get_param(p) })
        msg = command.to_stdmsgs_string(json.dumps(result))
        return command.to_commandoutput(msg.data)

    def handle_param_delete(self, req):  # Delete a parameter value
        payload = json.loads(req.input.payload)
        requested_key = payload["param"]
        status = { "status": "NOTFOUND"}
        if rospy.has_param(requested_key):
            if rosparam.get_param(requested_key) is not None:
                rosparam.delete_param(requested_key)
                status = { "status": "DELETED", "param": requested_key}
        msg = command.to_stdmsgs_string(json.dumps(status))
        return command.to_commandoutput(msg.data)


