import runpy
import pytest
import os

from dosaku import Config

samples_dir = os.path.join(Config()['DIR_PATHS']['PACKAGE'], 'dosaku', 'samples')
samples = [os.path.join(samples_dir, sample) for sample in os.listdir(samples_dir) if sample.endswith('.py')]


@pytest.mark.parametrize('sample', samples)
def test_sample_execution(sample):
    runpy.run_path(sample, run_name='__main__')
