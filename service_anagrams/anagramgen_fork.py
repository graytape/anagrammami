from random import randrange
import time

class Trie:
    """
    Trie (prefix tree) data structure for efficient word storage and lookup.
    Each node represents a character and paths from root to leaves form complete words.
    """
    
    def __init__(self):
        """Initialize the Trie with an empty root dictionary."""
        self.root = {}

    def add(self, word):
        """
        Add a word to the Trie.
        
        Args:
            word (str): The word to add to the Trie
        """
        self.__add(self.root, word[0], word[1:])

    def __add(self, node, prefix, suffix):
        """
        Private recursive method to add a word to the Trie.
        
        Args:
            node (dict): Current Trie node
            prefix (str): Current character to add
            suffix (str): Remaining characters of the word
        """
        if prefix not in node:
            node[prefix] = {}
        
        if suffix == "":
            # Empty string marks the end of a valid word
            node[prefix][suffix] = ""
        else:
            # Continue recursively with next character
            new_prefix = suffix[0]
            new_suffix = suffix[1:]
            self.__add(node[prefix], new_prefix, new_suffix)

    def __contains__(self, word):
        """
        Check if a word exists in the Trie.
        
        Args:
            word (str): The word to search for
            
        Returns:
            bool: True if word exists, False otherwise
        """
        word = list(word)
        index_string = "['" + "']['".join(word) + "']"
        try:
            child_nodes = eval("self.root"+index_string)
            if '' in child_nodes:
                return True
        except KeyError:
            pass
        return False


class AnagramGenerator:
    """
    Anagram generator that finds all possible word combinations
    using exactly the letters from a given string.
    """
    
    def __init__(self, corpus):
        """
        Initialize the generator with a word corpus.
        
        Args:
            corpus (list): List of words to use for generating anagrams
        """
        self.t = Trie()
        word_count = 0
        print(f"Loading corpus...")
        for word in corpus:
            word = word.rstrip()
            self.t.add(word)
            word_count += 1
        print(f"Loaded {word_count} words into Trie")

    def frequency_dict(self, string):
        """
        Create a frequency dictionary of characters in a string.
        
        Args:
            string (str): The string to analyze
            
        Returns:
            dict: Dictionary with characters as keys and frequencies as values
        """
        f = {}
        for letter in string:
            if letter not in f:
                f[letter] = 0
            f[letter] += 1
        return f

    def generate(self, string, max_results=10000, timeout=30):
        """
        Generate all possible anagrams of the given string, sorted to prioritize
        solutions with longer words first.
        
        Args:
            string (str): The string to generate anagrams for
            max_results (int): Maximum number of anagrams to generate (default: 10000)
            timeout (int): Maximum time in seconds before stopping (default: 30)
            
        Returns:
            list: List of anagrams, where each anagram is a list of words
        """
        # Normalize string: convert to lowercase and remove non-alphabetic characters
        string = string.lower()
        for c in string:
            if c not in 'abcdefghijklmnopqrstuvwxyz':
                string = string.replace(c, "")

        print(f"\n=== Starting anagram generation ===")
        print(f"Input string: '{string}' (length: {len(string)} letters)")
        print(f"Max results: {max_results}, Timeout: {timeout}s")
        
        anagrams = []
        f = self.frequency_dict(string)
        
        print(f"Letter frequencies: {f}")
        
        # Track generation progress
        start_time = time.time()
        stats = {
            'calls': 0,
            'completed_words': 0,
            'max_depth': 0
        }
        
        # Generate all anagrams with limits
        try:
            self.__generate(anagrams, self.t.root, [], "", f, 0, max_results, start_time, timeout, stats)
        except TimeoutError as e:
            print(f"\n⚠️  {e}")
        except MaxResultsError as e:
            print(f"\n⚠️  {e}")
        
        elapsed = time.time() - start_time
        print(f"\n=== Generation complete ===")
        print(f"String: {string}")
        print(f"Found {len(anagrams)} anagrams in {elapsed:.2f}s")
        print(f"Recursive calls: {stats['calls']}")
        print(f"Words completed: {stats['completed_words']}")
        print(f"Max recursion depth: {stats['max_depth']}")

        if len(anagrams) == 0:
            print("⚠️  No anagrams found. This could mean:")
            print("   - The word/phrase is too long for the corpus")
            print("   - The letter combination doesn't form valid words")
            return {
                'success': False,
                'n_results': 0,
                'anagrams': []
            }

        # Sort anagrams to prioritize longer words
        # First by average word length (descending)
        # Then by number of words (ascending - fewer words = longer words)
        print(f"Sorting results...")
        anagrams.sort(key=lambda phrase: (
            -sum(len(word) for word in phrase) / len(phrase),  # Average length descending
            len(phrase)  # Number of words ascending
        ))

        result = {
            'success'  : True,
            'n_results': len(anagrams),
            'recursion': stats['calls'],
            'words'    : stats['completed_words'],
            'anagrams' : anagrams
        }
        return result
        


    def __generate(self, anagrams, node, partial_anagram, current_word, f, depth, max_results, start_time, timeout, stats):
        """
        Private recursive method to generate anagrams with progress tracking and limits.
        
        Explores all possible combinations of valid words that use
        exactly the available letters in the frequency dictionary.
        
        Args:
            anagrams (list): Accumulator list to save found anagrams
            node (dict): Current node in the Trie
            partial_anagram (list): List of completed words so far
            current_word (str): Word being constructed
            f (dict): Frequency dictionary of remaining letters
            depth (int): Current recursion depth
            max_results (int): Maximum number of results before stopping
            start_time (float): Start timestamp for timeout checking
            timeout (int): Maximum seconds before timeout
            stats (dict): Statistics dictionary for tracking progress
        """
        # Update statistics
        stats['calls'] += 1
        stats['max_depth'] = max(stats['max_depth'], depth)
        
        # Check for timeout
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Generation stopped: timeout of {timeout}s exceeded")
        
        # Check for max results
        if len(anagrams) >= max_results:
            raise MaxResultsError(f"Generation stopped: reached max results ({max_results})")
        
        # Progress indicator every 100000 calls
        if stats['calls'] % 100000 == 0:
            elapsed = time.time() - start_time
            print(f"  Progress: {stats['calls']} calls, {len(anagrams)} anagrams found, {elapsed:.1f}s elapsed, depth: {depth}")
        
        # If we just completed a valid word
        if '' in node:
            stats['completed_words'] += 1
            next_partial_anagram = partial_anagram + [current_word]
            
            # If we've used all letters, we have a complete anagram
            if all([f[key] == 0 for key in f]):
                anagrams.append(next_partial_anagram)
                if len(anagrams) % 100 == 0:
                    print(f"  Found anagram #{len(anagrams)}: {' '.join(next_partial_anagram)}")
            else:
                # Otherwise, restart from root to search for next word
                self.__generate(anagrams, self.t.root, next_partial_anagram, "", f, depth + 1, max_results, start_time, timeout, stats)

        # Try each letter still available
        for prefix in f:
            if f[prefix] > 0:  # If letter is still available
                if prefix in node:  # If letter is a valid path in Trie
                    new_word = current_word + prefix
                    
                    # Condition to maintain lexicographic order and avoid duplicates
                    # New word must be >= last word in common prefix
                    if len(partial_anagram) == 0 or new_word >= partial_anagram[-1][:len(new_word)]:
                        # Use the letter (subtract from frequency)
                        f[prefix] -= 1
                        
                        # Recursion to continue building the word
                        self.__generate(anagrams, node[prefix], partial_anagram, new_word, f, depth + 1, max_results, start_time, timeout, stats)
                        
                        # Restore the letter for other combinations (backtracking)
                        f[prefix] += 1


class TimeoutError(Exception):
    """Exception raised when generation exceeds timeout limit."""
    pass


class MaxResultsError(Exception):
    """Exception raised when generation reaches max results limit."""
    pass