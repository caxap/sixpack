import unittest
from numbers import Number
from mock import MagicMock
from sixpack.db import REDIS, _key

from sixpack.models import Alternative

class TestAlternativeModel(unittest.TestCase):

    unit = True

    def setUp(self):
        self.redis = MagicMock(REDIS)
        self.client_id = 381

    def test_key(self):
        alt = Alternative('yes', 'show-something', self.redis)
        key = alt.key()
        self.assertEqual(key, 'sixpack:show-something:yes')

    def test_is_valid(self):
        valid = Alternative.is_valid('1')
        self.assertTrue(valid)

        unicode_valid = Alternative.is_valid(u'valid')
        self.assertTrue(unicode_valid)

    def test_is_not_valid(self):
        not_valid = Alternative.is_valid(1)
        self.assertFalse(not_valid)

        not_valid = Alternative.is_valid(':123:name')
        self.assertFalse(not_valid)

        not_valid = Alternative.is_valid('_123name')
        self.assertFalse(not_valid)

        not_valid = Alternative.is_valid('&123name')
        self.assertFalse(not_valid)

    def test_reset(self):
        alt = Alternative('yes', 'show-something', self.redis)
        alt.reset()
        self.redis.delete.assert_any_call(_key("conversion:{0}:{1}".format(alt.experiment_name, alt.name)))
        self.redis.delete.assert_any_call(_key("participation:{0}:{1}".format(alt.experiment_name, alt.name)))

    def test_delete(self):
        alt = Alternative('yes', 'show-something', self.redis)
        alt.delete()
        self.redis.delete.assert_called_once_with(alt.key())

    def test_is_control(self):
        pass

    def test_experiment(self):
        pass

    def test_participant_count(self):
        self.redis.bitcount.return_value = 1

        alt = Alternative('yes', 'show-something', self.redis)
        count = alt.participant_count()

        key = _key("participation:{0}:{1}".format(alt.experiment_name, alt.name))
        self.redis.bitcount.assert_called_once_with(key)
        self.assertTrue(isinstance(count, Number))

        self.redis.reset_mock()

    def test_conversion_count(self):
        self.redis.bitcount.return_value = 1

        alt = Alternative('yes', 'show-something', self.redis)
        count = alt.completed_count()

        key = _key("conversion:{0}:{1}".format(alt.experiment_name, alt.name))
        self.redis.bitcount.assert_called_once_with(key)
        self.assertTrue(isinstance(count, Number))

        self.redis.reset_mock()

    # TODO Test this
    def test_record_participation(self):
        pass
        # alt = Alternative('yes', 'show-something', self.redis)
        # alt.record_participation(self.client_id)

        # key = _key("participation:{0}:{1}".format(alt.experiment_name, alt.name))
        # self.redis.setbit.assert_called_once_with(key, self.client_id, 1)

    def test_record_conversion(self):
        alt = Alternative('yes', 'show-something', self.redis)
        alt.record_conversion(self.client_id)

        key = _key("conversion:{0}:{1}".format(alt.experiment_name, alt.name))
        self.redis.setbit.assert_called_once_with(key, self.client_id, 1)
