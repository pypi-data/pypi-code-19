# -*- coding: utf-8 -*-
import random
import re

import settings

## === Functions === ##
def clean(line):
    """ Strip a string of non-alphanumerics (except underscores).
    Can use to clean strings before using them in a database query.

    Args:
        line(unicode): String to clean.

    Returns:
        line(unicode): A string safe to use in a database query.

    Examples:
        >>> clean("Robert'); DROP TABLE Students;")
        RobertDROPTABLEStudents
        
    """
    return "".join(char for char in line if (char.isalnum() or "_" == char))

def parse_cases(text):
    """ Changes substring's letter case (uppercase, lowercase, start case, sentence case).

    Args:
        text(unicode): String to parse.
        
    """
    UPPER_PATTERN = fr"{settings.OPEN_UPPER}(.*?){settings.CLOSE_UPPER}"
    LOWER_PATTERN = fr"{settings.OPEN_LOWER}(.*?){settings.CLOSE_LOWER}"
    STARTCASE_PATTERN = fr"{settings.OPEN_STARTCASE}(.*?){settings.CLOSE_STARTCASE}"
    SENCASE_PATTERN = fr"{settings.OPEN_SENTENCE}(.*?){settings.CLOSE_SENTENCE}"
    
    for result in re.finditer(UPPER_PATTERN, text):
        ## Uppercase -> "ALL MY LIFE HAS BEEN A SERIES OF DOORS IN MY FACE."
        text = text.replace(result.group(), result.group(1).upper())

    for result in re.finditer(LOWER_PATTERN, text):
        ## Lowercase -> "all my life has been a series of doors in my face."
        text = text.replace(result.group(), result.group(1).lower())

    for result in re.finditer(STARTCASE_PATTERN, text):
        ## Startcase -> "All My Life Has Been A Series Of Doors In My Face."
        text = text.replace(result.group(), titlecase(result.group(1)))

    for result in re.finditer(SENCASE_PATTERN, text):
        ## Sentence case -> "All my life has been a series of doors in my face."
        newCase = result.group(1)
        
        for index, character in enumerate(newCase):
            if character.isalpha():
                text = text.replace(result.group(),
                                    newCase[:index] + newCase[index:].capitalize())
                break
        
        
    return text

def parse_choices(text):
    """ Chooses a random option in a given set.

    Args:
        text(unicode): String to parse. Options are enclosed in angle brackets,
            separated by a pipeline.

    Yields:
        newString(unicode): An option from the leftmost set of options is chosen
            for the string and updates accordingly.

    Raises:
        StopIteration: text's options are all chosen.

    Examples:
        >>> next(parse_choices("<Chocolates|Sandwiches> are the best!"))
        "Chocolates are the best!"

        >>> result = parse_choices("I would like some <cupcakes|ice cream>,
            <please|thanks>.")
        >>> for _ in result: print(next(result))
        I would like some <cupcakes|ice cream>, thanks.
        I would like some cupcakes, thanks.
        
    """
    OPEN_CHAR = settings.OPEN_CHOOSE
    CLOSE_CHAR = settings.CLOSE_CHOOSE
    ESCAPE_CHAR = settings.ESCAPE_CHAR
    SPLITTER = settings.SPLIT_CHOOSE
    done = False

    while not done:
        if OPEN_CHAR not in text or CLOSE_CHAR not in text:
            done = True
            
        level = 0
        escape_num = 0
        open_index = 0
        close_index = 0
        optionNum = 0
        options = []
        
        for index, char in enumerate(text):
            if OPEN_CHAR == char and not escape_num % 2:
                level += 1
                if 1 == level:
                    open_index = index
                    options.append([])
                elif level:
                    options[optionNum].append(char)
            elif CLOSE_CHAR == char and not escape_num % 2:
                level -= 1
                if 0 == level:
                    ## First and outermost level gathered.
                    close_index = index
                    break
                elif level:
                    options[optionNum].append(char)
            elif SPLITTER == char and not escape_num % 2:
                if 1 == level:
                    optionNum += 1
                    options.append([])
                elif level:
                    options[optionNum].append(char)
            elif ESCAPE_CHAR == char:
                escape_num += 1
                if level:
                    options[optionNum].append(char)
            else:
                escape_num = 0
                if level:
                    options[optionNum].append(char)
                
        tmp_block = text[open_index:close_index + 1]
        
        if 1 < len(tmp_block):
            text = text.replace(tmp_block, "".join(random.choice(options)))
        else:
            done = True
            
        yield text
    
def parse_optional(text):
    """ Chooses whether to omit a substring or not.

    Args:
        text(unicode): String to parse. Substring to be reviewed is enclosed in braces.

    Yields:
        text(unicode): The string with or without the leftmost substring,
            stripped of the braces.

    Raises:
        StopIteration: text's braces are fully parsed.

    Examples:
        >>> next(parse_optional("You're mean{ingful}."))
        "You're meaningful."

        >>> result = parse_optional("You're pretty{{ darn} awful}.")
        >>> for _ in result: print(next(result))
        You're pretty{ darn} awful.
        You're pretty awful.
        
    """
    OPEN_CHAR = settings.OPEN_OMIT
    CLOSE_CHAR = settings.CLOSE_OMIT
    ESCAPE_CHAR = settings.ESCAPE_CHAR
    done = False

    while not done:
        if OPEN_CHAR not in text or CLOSE_CHAR not in text:
            done = True
            
        level = 0
        escape_num = 0
        open_index = 0
        close_index = 0
        
        for index, char in enumerate(text):
            if OPEN_CHAR == char and not escape_num % 2:
                level += 1
                if 1 == level:
                    open_index = index
            elif CLOSE_CHAR == char and not escape_num % 2:
                level -= 1
                if 0 == level:
                    ## First and outermost level gathered.
                    close_index = index
                    break
            elif ESCAPE_CHAR == char:
                escape_num += 1
            else:
                escape_num = 0
                
        tmp_block = text[open_index:close_index + 1]
        
        if 1 < len(tmp_block):
            if random.getrandbits(1):
                text = "".join([text[:open_index], text[close_index + 1:]])
            else:
                text = "".join([text[:open_index], text[open_index + 1:close_index],
                                text[close_index + 1:]])
        else:
            done = True
            
        yield text

def parse_all(text):
    """ Parses special blocks of text and takes care of escape characters.
      - Makes a choice between multiple phrases (parse_choices)
      - Chooses whether to omit a phrase or not (parse_optional)
      - Changes the letter case of a phrase (parse_cases)

    Args:
        text(unicode): String to parse.

    Returns:
        text(unicode): Updated string.

    Examples:
        >>> parse_all("I'm {b}eating you{r <cake|homework>}.")
        I'm eating your homework.
        
    """
    if (settings.OPEN_OMIT in text
    and settings.CLOSE_OMIT in text):
        for result in parse_optional(text):
            text = result

    if (settings.OPEN_CHOOSE in text
    and settings.OPEN_CHOOSE in text):
        for result in parse_choices(text):
            text = result

    text = parse_cases(text)

    ## Parse escape characters.
    text = text.replace("{0}{0}".format(settings.ESCAPE_CHAR), settings.SENTINEL)
    text = text.replace(settings.ESCAPE_CHAR, "")
    text = text.replace(settings.SENTINEL, settings.ESCAPE_CHAR)

    return text

def regexp(expression, line):
    reg = re.compile(expression)

    if line:
        return reg.search(line) is not None

def titlecase(text):
    return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                  lambda mo: mo.group(0)[0].upper() +
                             mo.group(0)[1:].lower(),
                  text)
