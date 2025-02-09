import pytest
import repokid.cli.repokid_cli
import repokid.hooks
from repokid.hooks.loggers import log_during_repoable_calculation_batch_hooks
from repokid.role import Role
from repokid.tests.artifacts.hook import function_1, function_2
from repokid.tests.test_repokid_cli import ROLES


def func_a(input_dict):
    input_dict['value'] += 1
    return input_dict


def func_b(input_dict):
    input_dict['value'] += 1
    return input_dict


def func_c(input_dict):
    input_dict['value'] += 10
    return input_dict


def func_d(input_value):
    required_vals = ['a', 'b']
    if not all(val in input_value for val in required_vals):
        raise repokid.hooks.MissingHookParamaeter


def func_e(input_value):
    pass


class TestHooks(object):
    def test_call_hooks(self):
        hooks = {'TEST_HOOK': [func_a, func_b], 'NOT_CALLED': [func_c], 'MISSING_PARAMETER': [func_d],
                 'MISSING_OUTPUT': [func_e]}
        hook_args = {'value': 0}
        output_value = repokid.hooks.call_hooks(hooks, 'TEST_HOOK', hook_args)

        # func_a and func_b are called to increment 0 --> 2, func_c is not called
        assert output_value['value'] == 2

        # missing required parameter b
        with pytest.raises(repokid.hooks.MissingHookParamaeter):
            output_value = repokid.hooks.call_hooks(hooks, 'MISSING_PARAMETER', {'a': '1'})

        with pytest.raises(repokid.hooks.MissingOutputInHook):
            output_value = repokid.hooks.call_hooks(hooks, 'MISSING_OUTPUT', {'a': 1})

    def test_get_hooks(self):
        hooks_config = ['repokid.tests.artifacts.hook']
        hooks = repokid.cli.repokid_cli._get_hooks(hooks_config)

        # key is correct, both functions are loaded and in correct priority order
        assert hooks == {'TEST_HOOK': [function_1, function_2]}

    def test_implements_hook(self):
        def func_a():
            pass

        @repokid.hooks.implements_hook('DECORATOR_TEST', 1)
        def func_b():
            pass

        assert not hasattr(func_a, "_implements_hook")
        assert hasattr(func_b, "_implements_hook")
        assert func_b._implements_hook == {"hook_name": 'DECORATOR_TEST', "priority": 1}

    def test_log_during_repoable_calculation_batch_hooks(self):
        hooks = {'DURING_REPOABLE_CALCULATION_BATCH': [log_during_repoable_calculation_batch_hooks]}

        input_dict = {'role_batch': [Role(ROLES[0]), "def"], 'potentially_repoable_permissions': [], 'minimum_age': 1}

        with pytest.raises(repokid.hooks.MissingHookParamaeter):
            # role_batch', 'potentially_repoable_permissions', 'minimum_age'
            repokid.hooks.call_hooks(hooks, 'DURING_REPOABLE_CALCULATION_BATCH', input_dict)

        input_dict['role_batch'] = [Role(ROLES[0]), Role(ROLES[1]), Role(ROLES[2])]
        assert input_dict == repokid.hooks.call_hooks(hooks, 'DURING_REPOABLE_CALCULATION_BATCH', input_dict)
