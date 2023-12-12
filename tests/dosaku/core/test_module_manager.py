import pytest

from dosaku import ModuleManager, ServicePermissionRequired, ExecutorPermissionRequired
from dosaku.modules import BARTSummarizer, BARTZeroShotClassifier, Coder, GPT
from dosaku.types import TextClassification


def test_module_manager():
    """Test ModuleManager class."""
    article = (
        'Videos that say approved vaccines are dangerous and cause autism, cancer or infertility are among those that will '
        'be taken down, the company said. The policy includes the termination of accounts of anti-vaccine influencers. '
        'Tech giants have been criticised for not doing more to counter false health information on their sites.  '
        'In July, US President Joe Biden said social media platforms were largely responsible for people\'s scepticism in '
        'getting vaccinated by spreading misinformation, and appealed for them to address the issue. YouTube, which is '
        'owned by Google, said 130,000 videos were removed from its platform since last year, when it implemented a ban on '
        'content spreading misinformation about Covid vaccines.  In a blog post, the company said it had seen false claims '
        'about Covid jabs "spill over into misinformation about vaccines in general". The new policy covers long-approved '
        'vaccines, such as those against measles or hepatitis B. "We\'re expanding our medical misinformation policies '
        'on YouTube with new guidelines on currently administered vaccines that are approved and confirmed to be safe and '
        'effective by local health authorities and the WHO," the post said, referring to the World Health Organization.'
    )
    potential_topics = ['politics', 'sports', 'science', 'technology', 'entertainment', 'business', 'health', 'world']

    # Create a module manager, passing in which devices it should manage.
    mm = ModuleManager(devices='cuda:0')

    # Register any number of modules with the manager. They will not be loaded at this time.
    mm.register_builder('summarizer', builder=BARTSummarizer)
    mm.register_builder('classifier', builder=BARTZeroShotClassifier)
    mm.register_builder('coder', builder=Coder)
    mm.register_builder('gpt', builder=GPT)

    # Test overwriting registered builder
    mm.register_builder('summarizer', builder=BARTSummarizer)

    # Assert that requesting an unloaded module raises a RuntimeError.
    with pytest.raises(RuntimeError):
        _ = mm.module('summarizer')

    # Assert a RuntimeError is raised if we try to move a module that isn't loaded.
    with pytest.raises(RuntimeError):
        mm.move('summarizer', 'cpu')

    # Assert modules that aren't loaded return as None
    assert mm.module_location('summarizer') is None

    # Assert that modules can be loaded and/or moved to a device.
    mm.load('summarizer', device='cpu')
    mm.move('summarizer', device='cuda')
    mm.load('classifier', device='cuda', share_device=False)
    assert mm.module_location('classifier') == 'cuda:0'
    assert mm.module_location('summarizer') == 'cpu'

    # Assert that a RuntimeError is returned if we try to load a module onto a device that isn't being managed.
    with pytest.raises(RuntimeError):
        mm.load('classifier', device='cuda:1')

    # Make sure we can move a model onto the same device twice without an error (should raise a warning only)
    mm.move('classifier', device='cuda:0')
    mm.move('classifier', device='cuda:0')

    # Assert that a ServicePermissionRequired is raised if we try to load a service without permission
    with pytest.raises(ServicePermissionRequired):
        mm.load('gpt')

    # Assert that an ExecutorPermissionRequired is raised if we try to load an executor without permission
    with pytest.raises(ExecutorPermissionRequired):
        mm.load('coder', allow_services=True)

    # Assert that modules can both be loaded onto the same device.
    mm.load('summarizer', device='cuda:0', share_device=True)
    assert mm.module_location('classifier') == 'cuda:0'
    assert mm.module_location('summarizer') == 'cuda:0'
    assert 'summarizer' not in mm.modules_on_device('cpu')

    # Assert that modules can be used.
    summary = mm.module('summarizer').summarize(text=article, min_length=30, max_length=130)
    topic = mm.module('classifier').classify(text=summary, labels=potential_topics)
    assert isinstance(summary, str)
    assert isinstance(topic, TextClassification)

    # Assert that module attributes can be fetched.
    summarize = mm.get_module_attr('summarizer', 'summarize')
    summary = summarize(text=article, min_length=30, max_length=130)
    assert isinstance(summary, str)

    # Assert that module with dependencies will automatically load the dependencies
    mm.register_builder('classifier 2', builder=BARTZeroShotClassifier)
    mm.register_builder('summarizer with dependency', builder=BARTSummarizer, dependencies=['classifier 2'])
    mm.load('summarizer with dependency', device='cuda')
    assert 'classifier 2' in mm.modules

    # Assert that the manager can generate summaries:
    assert isinstance(mm.summary(), str)

    # Assert that modules can be moved off device.
    mm.move('summarizer', 'cpu')
    mm.move('classifier', 'cpu')
    assert mm.module_location('summarizer') == 'cpu'
    assert mm.module_location('classifier') == 'cpu'

    # Assert that modules can be removed.
    mm.unload('summarizer')
    mm.unload('classifier')
    assert 'summarizer' in mm.unloaded_modules
    assert 'classifier' in mm.unloaded_modules

    # Assert unloading an unloaded module raises a RuntimeError.
    with pytest.raises(RuntimeError):
        mm.unload('summarizer')

    # Test that the manager can load a module when memory runs out (by unloading all other modules on the device)
    # TODO: Test works but moving all gpu memory to the cpu crashes the test runner. Need to find a cleaner way to test.
    """
    for i in range(50):
        name = 'classifier' + str(i)
        print(f'Loading {name} onto cuda:0')
        mm.register_builder(name, builder=BARTZeroShotClassifier)
        mm.load(name, device='cuda:0', share_device=True, force_device=True)
        assert mm.module_location(name) == 'cuda:0'

        if mm.num_modules_on_device('cuda:0') == 1:
            break
    """

if __name__ == '__main__':
    test_module_manager()
