# This sample demonstrates how to use the ModuleManager class to manage multiple modules across a set of GPU resources.

from dosaku.core.module_manager import ModuleManager
from dosaku.modules import BARTSummarizer, BARTZeroShotClassifier


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
module_manager = ModuleManager(devices=['cuda:0'])

# Register any number of modules with the manager. They will not be loaded at this time.
module_manager.register_builder('summarizer', builder=BARTSummarizer)
module_manager.register_builder('classifier', builder=BARTZeroShotClassifier)

# summarizer = module_manager.module('summarizer')  # RuntimeError: Module summarizer is not loaded. Load it first.

# Load the modules.
# You may use 'cuda' as a device name to load the module onto any available (unused) cuda device.
# You may try to share GPU resources by setting share_device=True. In the case where both models cannot be loaded onto
# the same device, whether the new model is loaded onto the device or not is determined by force_device. If
# force_device is True, all modules currently on the device will be moved to the cpu to allow the new model to load.
summarizer = module_manager.load('summarizer', device='cuda')  # loads to the first available cuda device
classifier = module_manager.load('classifier', device='cuda:0', share_device=True, force_device=True)

# You can check to see where each model ended up with:
print(f'cuda:0 currently holds: {module_manager.modules_on_device("cuda:0")}')  # ['summarizer', 'classifier']
print(f'classifier is currently located on the device \"{module_manager.module_location("classifier")}\"')  # 'cuda:0'

# Or simply print a summary of the current state of the manager:
print(module_manager.summary())

# Use the modules.
summary = summarizer.summarize(text=article, min_length=30, max_length=130)
topic = classifier.classify(text=summary, labels=potential_topics)

print(f'Summary: {summary}')
print(f'Topic: {topic}')
