\* test123 *\
Minimize
OBJ: x + 4 y + 9 z + w + 0.9 _C1_elastic_SubProblem_pos_penalty_var
 - 0.9 _C1_elastic_SubProblem_neg_penalty_var
Subject To
_C1_elastic_SubProblem_Constraint: w + _C1_elastic_SubProblem_neg_penalty_var
 + _C1_elastic_SubProblem_pos_penalty_var >= -1
c1: x + y <= 5
c2: x + z >= 10
c3: - y + z = 7
Bounds
-inf <= _C1_elastic_SubProblem_neg_penalty_var <= 0
x <= 4
-1 <= y <= 1
w free
End
