__author__ = 'pwwpcheng'

import datetime
from wsme import types as wtypes
from wsme import wsattr

class DictToObj:
    '''
    Convert python dictionary to python object.
    '''
    def __init__(self, **entries):
        self.__dict__.update(entries)


# class AdvEnum(wtypes.wsproperty):
#     '''
#     This class is copied from Ceilometer project.
#     Source location: /ceilometer/api/controllers/v2/base.py
#     '''
#     """Handle default and mandatory for wtypes.Enum."""
#     def __init__(self, name, *args, **kwargs):
#         self._name = '_advenum_%s' % name
#         self._default = kwargs.pop('default', None)
#         mandatory = kwargs.pop('mandatory', False)
#         enum = wtypes.Enum(*args, **kwargs)
#         super(AdvEnum, self).__init__(datatype=enum, fget=self._get,
#                                       fset=self._set, mandatory=mandatory)
#
#     def _get(self, parent):
#         if hasattr(parent, self._name):
#             value = getattr(parent, self._name)
#             return value or self._default
#         return self._default
#
#     def _set(self, parent, value):
#         try:
#             if self.datatype.validate(value):
#                 setattr(parent, self._name, value)
#         except ValueError as e:
#             raise wsme.exc.InvalidInput(self._name.replace('_advenum_', '', 1),
#                                         value, e)


states = ["ok", "alarm", "insufficient data"]
state_enum = wtypes.Enum(str, *states)
severities = ["low", "moderate", "critical"]
severity_enum = wtypes.Enum(str, *severities)

# class Alarm:
#     """Representation of an alarm.
#     Copied from Ceilometer project.
#     Source location: /ceilometer/api/controllers/v2/alarms.py
#
#     .. note::
#         combination_rule and threshold_rule are mutually exclusive. The *type*
#         of the alarm should be set to *threshold* or *combination* and the
#         appropriate rule should be filled.
#     """
#
#     alarm_id = ''
#     "The UUID of the alarm"
#
#     name = ''
#     "The name for the alarm"
#
#     description = ''  # provide a default
#     "The description of the alarm"
#
#     enabled = wsattr(bool, default=True)
#     "This alarm is enabled?"
#
#     ok_actions = wsattr([wtypes.text], default=[])
#     "The actions to do when alarm state change to ok"
#
#     alarm_actions = wsattr([wtypes.text], default=[])
#     "The actions to do when alarm state change to alarm"
#
#     insufficient_data_actions = wsattr([wtypes.text], default=[])
#     "The actions to do when alarm state change to insufficient data"
#
#     repeat_actions = wsattr(bool, default=False)
#     "The actions should be re-triggered on each evaluation cycle"
#
#     type = base.AdvEnum('type', str, *ALARMS_RULES.names(),
#                         mandatory=True)
#     "Explicit type specifier to select which rule to follow below."
#
#     time_constraints = wtypes.wsattr([AlarmTimeConstraint], default=[])
#     """Describe time constraints for the alarm"""
#
#     # These settings are ignored in the PUT or POST operations, but are
#     # filled in for GET
#     project_id = wtypes.text
#     "The ID of the project or tenant that owns the alarm"
#
#     user_id = wtypes.text
#     "The ID of the user who created the alarm"
#
#     timestamp = datetime.datetime
#     "The date of the last alarm definition update"
#
#     state = base.AdvEnum('state', str, *states,
#                          default='insufficient data')
#     "The state offset the alarm"
#
#     state_timestamp = datetime.datetime
#     "The date of the last alarm state changed"
#
#     severity = base.AdvEnum('severity', str, *severity_kind,
#                             default='low')
#     "The severity of the alarm"

