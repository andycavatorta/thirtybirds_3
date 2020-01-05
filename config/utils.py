#import imp
#combined_settings = imp.new_module(name)

def collate(base_settings_module, optional_settings_module):
    base_settings_classnames = [i for i in dir(base_settings_module) if not (i[:2]=="__" and i[-2:]=="__")] 
    optional_settings_classnames = [i for i in dir(optional_settings_module) if not (i[:2]=="__" and i[-2:]=="__")]
    for optional_settings_class in optional_settings_classnames:
        if optional_settings_class not in base_settings_classnames:
            setattr(base_settings_module, optional_settings_class, getattr(optional_settings_module, optional_settings_class))
        else:
            base_settings_class_ref = getattr(base_settings_module, optional_settings_class)
            optional_settings_class_ref = getattr(optional_settings_module, optional_settings_class)
            # todo: it would be more concise and idiomatic to do the following with multiple inheritance.  if possible.
            optional_settings_class_variable_names = [attr for attr in dir(optional_settings_class_ref) if not callable(getattr(optional_settings_class_ref, attr)) and not attr.startswith("__")]
            for optional_settings_class_variable_name in optional_settings_class_variable_names:
                setattr(base_settings_class_ref, optional_settings_class_variable_name, getattr(optional_settings_class_ref, optional_settings_class_variable_name))
