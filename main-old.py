from collections import defaultdict
from typing import Tuple
from collections import deque
# import google.generativeai as genai

class Node:
    def __init__(self, value: int, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

def is_palandrome(s: str) -> bool:
    """
    Check if the given string is a palindrome.
    
    A palindrome reads the same forwards and backwards, ignoring case and non-alphanumeric characters.
    
    :param s: The string to check.
    :return: True if the string is a palindrome, False otherwise.
    """
    # Normalize the string: remove non-alphanumeric characters and convert to lowercase
    normalized_str = ''.join(char.lower() for char in s if char.isalnum())
    
    # Check if the normalized string is equal to its reverse
    return normalized_str == normalized_str[::-1]

def is_palandrome_2(s: str) -> bool:
    l, r = 0, len(s)-1
    while l < r:
        while l < r and not s[l].isalnum():
            l += 1
        while l < r and not s[r].isalnum():
            r -= 1
        if s[l].lower() != s[r].lower():
            return False
        l += 1
        r -= 1
    return True

def longest_subtring_without_repeating_characters(s: str) -> Tuple [int, str]:
    """
    Find the length of the longest substring without repeating characters.
    
    :param s: The input string.
    :return: Length of the longest substring without repeating characters.
    """
    longest = 0
    l = 0
    counter: dict[str, int] = defaultdict(int)
    for r in range(len(s)):
        counter[s[r]] += 1
        print(f"Counter after adding {s[r]}: {counter}")
        while counter[s[r]]> 1:
            counter[s[l]] -=1
            l +=1
            print(f"Character {s[l]} at index {l} is repeating, moving left pointer")
            
        print(f"Current substring: {s[l:r+1]}, length: {r-l+1}")
        longest = max(longest, r-l+1)
    return longest, s[l:r+1]

def level_order_traversal(root: Node) -> list[list[int]]:
    result = []
    queue = deque([root])
    while len(queue) > 0:
        n = len(queue)
        new_level = []
        for _ in range(n):
            node = queue.popleft()
            new_level.append(node.value)
            for child in [node.left, node.right]:
                if child is not None:
                    queue.append(child)
        result.append(new_level)
    return result


def gemini_method():
    """
    Example method to demonstrate the use of a method.
    This is a placeholder for any specific functionality you want to implement.
    """
 

    client = genai.Client()
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents="What is the meaning of life?"
    )
    print(result.embeddings)

if __name__ == "__main__":
    test_strings = 'abcdbefgh'  # Example string to test
    length, substring = longest_subtring_without_repeating_characters(test_strings)
    print(f"Longest substring without repeating characters: {substring}, length: {length}")
    
    tree = Node(1, Node(2, Node(4), Node(5)), Node(3, None, Node(6)))
    print("Level order traversal of the tree:")
    for level in level_order_traversal(tree):
        print(level)
        
    nums = [1,2,3,4]
    squares = list(map(lambda x: x**3, nums))    
    print(f"Squares: {squares}")



    # gemini_method()