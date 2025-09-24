# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from cdktf_cdktf_provider_google.dialogflow_cx_agent import DialogflowCxAgent
from cdktf_cdktf_provider_google.dialogflow_cx_webhook import DialogflowCxWebhook

from cdktf_cdktf_provider_google.dialogflow_cx_entity_type import (
    DialogflowCxEntityType,
    DialogflowCxEntityTypeEntities,
    DialogflowCxEntityTypeExcludedPhrases,
)

from cdktf_cdktf_provider_google.dialogflow_cx_intent import (
    DialogflowCxIntent,
    DialogflowCxIntentParameters,
    DialogflowCxIntentTrainingPhrases,
    DialogflowCxIntentTrainingPhrasesParts,
)


from cdktf_cdktf_provider_google.dialogflow_cx_flow import (
    DialogflowCxFlow,
    DialogflowCxFlowEventHandlers,
    DialogflowCxFlowTransitionRoutes,
)

from cdktf_cdktf_provider_google.dialogflow_cx_page import (
    DialogflowCxPage,
    DialogflowCxPageEventHandlers,
    DialogflowCxPageFormParameters,
    DialogflowCxPageFormParametersFillBehaviorRepromptEventHandlers,
    DialogflowCxPageTransitionRoutes,
)


def cx_msg_condition_action(self, data, resource, param):
    self.tf_parameters_list(data, resource, param + ["messages"])
    self.tf_parameters_list(data, resource, param + ["conditional_cases"])
    self.tf_parameters_list(data, resource, param + ["set_parameter_actions"])


# fmt: off

def create_cx(self, cx):
    """creates cx"""
    name = cx["display_name"]
    cx["project"] = self.tf_ref("project", cx["project"])

    self.created["cx"][name] = DialogflowCxAgent(self, f"cx_{name}", **cx)


def generate_cx(self, my_resource, resource):
    """creates cx"""
    for data in self.eztf_config.get(my_resource, []):
        create_cx(self, data)


def create_cx_webhook(self, cx_webhook):
    """creates cx_webhook"""
    name = cx_webhook["display_name"]
    cx_webhook["project"] = self.tf_ref("project", cx_webhook["project"])

    cx_webhook["parent"] = self.tf_ref("cx", cx_webhook["parent"])

    self.created["cx_webhook"][name] = DialogflowCxWebhook(
        self, f"cx_webhook_{name}", **cx_webhook
    )


def generate_cx_webhook(self, my_resource, resource):
    """creates cx_webhook"""
    for data in self.eztf_config.get(my_resource, []):
        create_cx_webhook(self, data)


def create_cx_entity_type(self, cx_entity_type):
    """creates cx_entity_type"""
    name = cx_entity_type["display_name"]
    cx_entity_type["project"] = self.tf_ref("project", cx_entity_type["project"])
    cx_entity_type["parent"] = self.tf_ref("cx", cx_entity_type["parent"])

    self.tf_param_list(cx_entity_type, "entities", DialogflowCxEntityTypeEntities)
    self.tf_param_list(cx_entity_type, "excluded_phrases", DialogflowCxEntityTypeExcludedPhrases)

    self.created["cx_entity_type"][name] = DialogflowCxEntityType(
        self, f"cx_entity_type_{name}", **cx_entity_type
    )


def generate_cx_entity_type(self, my_resource, resource):
    """creates cx_entity_type"""
    for data in self.eztf_config.get(my_resource, []):
        create_cx_entity_type(self, data)


def create_cx_intent(self, cx_intent):
    """creates cx_intent"""
    name = cx_intent["display_name"]
    cx_intent["project"] = self.tf_ref("project", cx_intent["project"])
    cx_intent["parent"] = self.tf_ref("cx", cx_intent["parent"])

    
    for tp in cx_intent.get("training_phrases",[]):
        self.tf_param_list(tp, "parts", DialogflowCxIntentTrainingPhrasesParts)
    self.tf_param_list(cx_intent, "parameters", DialogflowCxIntentParameters)
    self.tf_param_list(cx_intent, "training_phrases", DialogflowCxIntentTrainingPhrases)

    self.created["cx_intent"][name] = DialogflowCxIntent(
        self, f"cx_intent_{name}", **cx_intent
    )


def generate_cx_intent(self, my_resource, resource):
    """creates cx_intent"""
    for data in self.eztf_config.get(my_resource, []):
        create_cx_intent(self, data)



# cdktf_cdktf_provider_google.dialogflow_cx_flow
# event_handlers
# event_handlers_trigger_fulfillment_conditional_cases
# event_handlers_trigger_fulfillment_messages
# event_handlers_trigger_fulfillment_set_parameter_actions
# transition_routes
# transition_routes_trigger_fulfillment_conditional_cases
# transition_routes_trigger_fulfillment_messages
# transition_routes_trigger_fulfillment_set_parameter_actions

def create_cx_flow(self, cx_flow):
    """creates cx_flow"""
    name = cx_flow["display_name"]
    cx_flow["project"] = self.tf_ref("project", cx_flow["project"])
    cx_flow["parent"] = self.tf_ref("cx", cx_flow["parent"])

    for eh in cx_flow.get("event_handlers", []):
        cx_msg_condition_action(self, eh.get("trigger_fulfillment"), ["event_handlers", "trigger_fulfillment"])
    self.tf_param_list(cx_flow, "event_handlers", DialogflowCxFlowEventHandlers)

    for tr in cx_flow.get("transition_routes", []):
        cx_msg_condition_action(self, tr.get("trigger_fulfillment"), ["transition_routes", "trigger_fulfillment"])
    self.tf_param_list(cx_flow, "transition_routes", DialogflowCxFlowTransitionRoutes)

    self.created["cx_flow"][name] = DialogflowCxFlow(self, f"cx_flow_{name}", **cx_flow)


def generate_cx_flow(self, my_resource, resource):
    """creates cx_flow"""
    for data in self.eztf_config.get(my_resource, []):
        create_cx_flow(self, data)


# cdktf_cdktf_provider_google.dialogflow_cx_page
# entry_fulfillment_conditional_cases
# entry_fulfillment_messages
# entry_fulfillment_set_parameter_actions
# event_handlers
# event_handlers_trigger_fulfillment_conditional_cases
# event_handlers_trigger_fulfillment_messages
# event_handlers_trigger_fulfillment_set_parameter_actions
# form_parameters_fill_behavior_initial_prompt_fulfillment_conditional_cases
# form_parameters_fill_behavior_initial_prompt_fulfillment_messages
# form_parameters_fill_behavior_initial_prompt_fulfillment_set_parameter_actions
# form_parameters_fill_behavior_reprompt_event_handlers
# form_parameters_fill_behavior_reprompt_event_handlers_trigger_fulfillment_conditional_cases
# form_parameters_fill_behavior_reprompt_event_handlers_trigger_fulfillment_messages
# form_parameters_fill_behavior_reprompt_event_handlers_trigger_fulfillment_set_parameter_actions
# form_parameters
# transition_routes
# transition_routes_trigger_fulfillment_conditional_cases
# transition_routes_trigger_fulfillment_messages
# transition_routes_trigger_fulfillment_set_parameter_actions

def create_cx_page(self, cx_page):
    """creates cx_page"""
    name = cx_page["display_name"]
    cx_page["project"] = self.tf_ref("project", cx_page["project"])
    cx_page["parent"] = self.tf_ref("cx", cx_page["parent"])

    cx_msg_condition_action(self, cx_page.get("entry_fulfillment"), ["entry_fulfillment"])

    for eh in cx_page.get("event_handlers", []):
        cx_msg_condition_action(self, eh.get("trigger_fulfillment"), ["event_handlers", "trigger_fulfillment"])
    self.tf_param_list(cx_page, "event_handlers", DialogflowCxPageEventHandlers)
    
    for tr in cx_page.get("transition_routes", []):
        cx_msg_condition_action(self, tr.get("trigger_fulfillment"), ["transition_routes", "trigger_fulfillment"])
    self.tf_param_list(cx_page, "transition_routes", DialogflowCxPageTransitionRoutes)

    for fp in cx_page.get("form", {}).get("parameters", []):
        nest_keys = ["form", "parameters", "fill_behavior"]
        for pfeh in fp.get("fill_behavior", {}).get("reprompt_event_handlers", []):
            cx_msg_condition_action(self, pfeh.get("trigger_fulfillment"), nest_keys + ["reprompt_event_handlers", "trigger_fulfillment"])
        self.tf_param_list(fp.get("fill_behavior"), "reprompt_event_handlers", DialogflowCxPageFormParametersFillBehaviorRepromptEventHandlers)

        cx_msg_condition_action(self, fp.get("fill_behavior", {}).get("initial_prompt_fulfillment"), nest_keys + ["initial_prompt_fulfillment"])

    self.tf_param_list(cx_page.get("form"), "parameters", DialogflowCxPageFormParameters)

    self.created["cx_page"][name] = DialogflowCxPage(self, f"cx_page_{name}", **cx_page)


def generate_cx_page(self, my_resource, resource):
    """creates cx_page"""
    for data in self.eztf_config.get(my_resource, []):
        create_cx_page(self, data)
