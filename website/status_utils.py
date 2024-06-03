from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet

lemmatizer = WordNetLemmatizer()

software_related_words = [
    'software', 'install', 'update', 'delete', 'application', 'program'
]
software_specific_names = [
    'Excel', 'Outlook', 'Word', 'Teams', 'OneDrive', 'One Drive'
]

account_related_words = [
    'account', 'access', 'remote', 'password', 'username'
]

network_related_words = [
    'network', 'connect', 'configure', 'setup', 'admin', 'manage', 'internet', 'cooling'
]

device_repair_words = [
    'break', 'disappear', 'load', 'stop', 'freeze', 'work', 'respond', 'jam', 'correct', 'repair',
    'restore', 'error', 'fix', 'help'
]
device_management_words = [
    'screen', 'monitor', 'headphones', 'microphone', 'laptop', 'computer', 'projector', 'keyboard',
    'buy', 'quality', 'remove', 'cord', 'organise', 'phone', 'printer', 'socket', 'hdmi', 'mouse', 'cable', 'printhead'
]

file_management_words = [
    'file', 'folder', 'export', 'import', 'load', 'open', 'delete', 'scan', 'data'
]

communication_words = [
    'mail', 'letter', 'list', 'receive', 'dispatch', 'mailbox'
]

security_words = [
    'suspicious', 'link', 'phishing', 
]

software_lemmas = {lemmatizer.lemmatize(word, pos=wordnet.VERB) for word in software_related_words}
software_specific_names_set = set(word.lower() for word in software_specific_names)
account_lemmas = {lemmatizer.lemmatize(word, pos=wordnet.VERB) for word in account_related_words}
network_lemmas = {lemmatizer.lemmatize(word, pos=wordnet.VERB) for word in network_related_words}
device_repair_lemmas = {lemmatizer.lemmatize(word, pos=wordnet.VERB) for word in device_repair_words}
device_management_lemmas = {lemmatizer.lemmatize(word, pos=wordnet.VERB) for word in device_management_words}
file_management_lemmas = {lemmatizer.lemmatize(word, pos=wordnet.VERB) for word in file_management_words}
communication_lemmas = {lemmatizer.lemmatize(word, pos=wordnet.VERB) for word in communication_words}
security_lemmas = {lemmatizer.lemmatize(word, pos=wordnet.VERB) for word in security_words}

def determine_task_type(request_text):

    words = word_tokenize(request_text.lower())
    lemmas = {lemmatizer.lemmatize(word, pos=wordnet.VERB) for word in words}
    print(lemmas)

    if lemmas & security_lemmas:
        return 11 
    
    if lemmas & file_management_lemmas:
        return 9 
    
    if lemmas & communication_lemmas:
        return 10 
    
    if lemmas & software_lemmas or lemmas & software_specific_names_set:
        return 1 #software management

    if lemmas & account_lemmas:
        return 2 # account management
    
    if lemmas & device_repair_lemmas:
        return 7 
    
    if lemmas & device_management_lemmas:
        return 8 
    
    if lemmas & network_lemmas:
        return 4 # network management
    
    
    

    return 3 #Other


