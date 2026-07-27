import unittest
from diagnostics_manager import DiagnosticsManager
from version import APP_VERSION

class Rc44CommandIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.published=[]
        self.d=DiagnosticsManager('york/ac2/diagnostic',APP_VERSION,lambda t,p,r=True:self.published.append((t,p,r)) or True)

    def test_deferred_does_not_reduce_success_rate(self):
        self.d.command_count=4
        self.d.command_deferred_count=1
        self.d.command_failure_count=0
        self.assertEqual(self.d.command_success_rate,100.0)

    def test_real_failure_reduces_success_rate(self):
        self.d.command_count=4
        self.d.command_deferred_count=1
        self.d.command_failure_count=1
        self.assertEqual(self.d.command_success_rate,66.7)

    def test_not_applicable_does_not_reduce_success_rate(self):
        self.d.command_count=5
        self.d.command_deferred_count=1
        self.d.command_not_applicable_count=1
        self.d.command_failure_count=0
        self.assertEqual(self.d.command_success_rate,100.0)

    def test_deferred_resets_transaction_timing(self):
        self.d.publish_command(command_json='{"temperature": 24}',result='deferred')
        values={t.rsplit('/',1)[-1]:p for t,p,_ in self.published}
        self.assertEqual(values['last_command_duration'],'0')
        self.assertEqual(values['last_transaction_id'],'0')

if __name__=='__main__': unittest.main()
