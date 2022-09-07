## Practice Questions

### Set Operations
#### Problem
In a school, there are total 20 students numbered from 1 to 20. You’re given three lists named ‘C’, ‘F’, and ‘H’, representing students who play cricket, football, and hockey, respectively. Based on this information, find out and print the following: 
- Students who play all the three sports
- Students who play both cricket and football but don’t play hockey
- Students who play exactly two of the sports
- Students who don’t play any of the three sports

Format: \n
Input: \n
3 lists containing numbers (ranging from 1 to 20) representing students who play cricket, football and hockey respectively.
Output:
4 different lists containing the students according to the constraints provided in the questions.

Note: Make sure you sort the final lists (in an ascending order) that you get before printing them; otherwise your answer might not match the test-cases.

Examples:
Input 1:
[2, 5, 9, 12, 13, 15, 16, 17, 18, 19]
[2, 4, 5, 6, 7, 9, 13, 16]
[1, 2, 5, 9, 10, 11, 12, 13, 15]
Output 1:
[2, 5, 9, 13]
[16]
[12, 15, 16]
[3, 8, 14, 20]


#### Solution:

    # Read the three input lists, i.e. 'C', 'F', and 'H'.

    C = input_list[0]
    F = input_list[1]
    H = input_list[2]

    C = set(C)
    F = set(F)
    H = set(H)
    A = set([i for i in range(1,21)])

    print(sorted(C.intersection(F).intersection(H)))
    print(sorted(C.intersection(F).difference(H)))
    print(sorted((C.intersection(F).difference(H)).union(F.intersection(H).difference(C)).union(H.intersection(C).difference(F))))
    print(sorted(C.union(F).union(H).symmetric_difference(A)))


