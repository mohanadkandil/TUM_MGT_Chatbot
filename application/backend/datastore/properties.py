# TODO: Further refine what properties to store
# Unstructured provides quite a lot of metadata that we could add here
# Some of this metadata we will need to generate with AI

# The actual text content of the chunk is the only vectorized property
TEXT = "text"
# The filepath of the owning file in OneDrive
FILEPATH = "filepath"
# The hash of the owning file
# We can use this for synchronization
HASH = "hash"
# The links contained in this chunk (from Unstructured)
# This might be useful to programmatically display relevant links to the user
LINKS = "links"
# The language of the owning file / this chunk (from Unstructured)
# Should only ever be English or German
LANGUAGE = "language"
# The degree program the owning file is associated with
# We should also include a category for no degree program / general information
# We will probably need to use AI to figure this out automatically
DEGREE_PROGRAM = "degree_program"
# The topic of the owning file
# We will probably need to use AI here too
TOPIC = "topic"
