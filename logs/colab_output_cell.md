 ---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
/tmp/ipykernel_7003/3741712581.py in <cell line: 0>()
    101     model = row["model"]
    102     variants = ["C1", "C2", "C3", "C4"] if model == "llama" else ["Q1-W", "Q2", "Q3-Ref", "Q4-Ref"]
--> 103     subset = energy.query("model == @model and context == 4096 and regime == @row['regime'] and source_variant in @variants")
    104     pivot = subset.pivot(index="block", columns="source_variant", values=row["metric"])
    105     values = (pivot[variants[3]] - pivot[variants[2]]) - (pivot[variants[1]] - pivot[variants[0]])

24 frames/usr/local/lib/python3.12/dist-packages/pandas/core/frame.py in query(self, expr, inplace, **kwargs)
   4821         kwargs["level"] = kwargs.pop("level", 0) + 1
   4822         kwargs["target"] = None
-> 4823         res = self.eval(expr, **kwargs)
   4824 
   4825         try:

/usr/local/lib/python3.12/dist-packages/pandas/core/frame.py in eval(self, expr, inplace, **kwargs)
   4947         kwargs["resolvers"] = tuple(kwargs.get("resolvers", ())) + resolvers
   4948 
-> 4949         return _eval(expr, inplace=inplace, **kwargs)
   4950 
   4951     def select_dtypes(self, include=None, exclude=None) -> Self:

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/eval.py in eval(expr, parser, engine, local_dict, global_dict, resolvers, level, target, inplace)
    334         )
    335 
--> 336         parsed_expr = Expr(expr, engine=engine, parser=parser, env=env)
    337 
    338         if engine == "numexpr" and (

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in __init__(self, expr, engine, parser, env, level)
    807         self.parser = parser
    808         self._visitor = PARSERS[parser](self.env, self.engine, self.parser)
--> 809         self.terms = self.parse()
    810 
    811     @property

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in parse(self)
    826         Parse an expression.
    827         """
--> 828         return self._visitor.visit(self.expr)
    829 
    830     @property

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in visit(self, node, **kwargs)
    410         method = f"visit_{type(node).__name__}"
    411         visitor = getattr(self, method)
--> 412         return visitor(node, **kwargs)
    413 
    414     def visit_Module(self, node, **kwargs):

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in visit_Module(self, node, **kwargs)
    416             raise SyntaxError("only a single expression is allowed")
    417         expr = node.body[0]
--> 418         return self.visit(expr, **kwargs)
    419 
    420     def visit_Expr(self, node, **kwargs):

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in visit(self, node, **kwargs)
    410         method = f"visit_{type(node).__name__}"
    411         visitor = getattr(self, method)
--> 412         return visitor(node, **kwargs)
    413 
    414     def visit_Module(self, node, **kwargs):

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in visit_Expr(self, node, **kwargs)
    419 
    420     def visit_Expr(self, node, **kwargs):
--> 421         return self.visit(node.value, **kwargs)
    422 
    423     def _rewrite_membership_op(self, node, left, right):

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in visit(self, node, **kwargs)
    410         method = f"visit_{type(node).__name__}"
    411         visitor = getattr(self, method)
--> 412         return visitor(node, **kwargs)
    413 
    414     def visit_Module(self, node, **kwargs):

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in visit_BoolOp(self, node, **kwargs)
    744 
    745         operands = node.values
--> 746         return reduce(visitor, operands)
    747 
    748 

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in visitor(x, y)
    738         def visitor(x, y):
    739             lhs = self._try_visit_binop(x)
--> 740             rhs = self._try_visit_binop(y)
    741 
    742             op, op_class, lhs, rhs = self._maybe_transform_eq_ne(node, lhs, rhs)

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in _try_visit_binop(self, bop)
    733         if isinstance(bop, (Op, Term)):
    734             return bop
--> 735         return self.visit(bop)
    736 
    737     def visit_BoolOp(self, node, **kwargs):

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in visit(self, node, **kwargs)
    410         method = f"visit_{type(node).__name__}"
    411         visitor = getattr(self, method)
--> 412         return visitor(node, **kwargs)
    413 
    414     def visit_Module(self, node, **kwargs):

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in visit_Compare(self, node, **kwargs)
    717             op = self.translate_In(ops[0])
    718             binop = ast.BinOp(op=op, left=node.left, right=comps[0])
--> 719             return self.visit(binop)
    720 
    721         # recursive case: we have a chained comparison, a CMP b CMP c, etc.

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in visit(self, node, **kwargs)
    410         method = f"visit_{type(node).__name__}"
    411         visitor = getattr(self, method)
--> 412         return visitor(node, **kwargs)
    413 
    414     def visit_Module(self, node, **kwargs):

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in visit_BinOp(self, node, **kwargs)
    530 
    531     def visit_BinOp(self, node, **kwargs):
--> 532         op, op_class, left, right = self._maybe_transform_eq_ne(node)
    533         left, right = self._maybe_downcast_constants(left, right)
    534         return self._maybe_evaluate_binop(op, op_class, left, right)

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in _maybe_transform_eq_ne(self, node, left, right)
    452             left = self.visit(node.left, side="left")
    453         if right is None:
--> 454             right = self.visit(node.right, side="right")
    455         op, op_class, left, right = self._rewrite_membership_op(node, left, right)
    456         return op, op_class, left, right

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in visit(self, node, **kwargs)
    410         method = f"visit_{type(node).__name__}"
    411         visitor = getattr(self, method)
--> 412         return visitor(node, **kwargs)
    413 
    414     def visit_Module(self, node, **kwargs):

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/expr.py in visit_Subscript(self, node, **kwargs)
    576         value = self.visit(node.value)
    577         slobj = self.visit(node.slice)
--> 578         result = pd_eval(
    579             slobj, local_dict=self.env, engine=self.engine, parser=self.parser
    580         )

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/eval.py in eval(expr, parser, engine, local_dict, global_dict, resolvers, level, target, inplace)
    355         eng = ENGINES[engine]
    356         eng_inst = eng(parsed_expr)
--> 357         ret = eng_inst.evaluate()
    358 
    359         if parsed_expr.assigner is None:

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/engines.py in evaluate(self)
     79 
     80         # make sure no names in resolvers and locals/globals clash
---> 81         res = self._evaluate()
     82         return reconstruct_object(
     83             self.result_type, res, self.aligned_axes, self.expr.terms.return_type

/usr/local/lib/python3.12/dist-packages/pandas/core/computation/engines.py in _evaluate(self)
    119         scope = env.full_scope
    120         _check_ne_builtin_clash(self.expr)
--> 121         return ne.evaluate(s, local_dict=scope)
    122 
    123 

/usr/local/lib/python3.12/dist-packages/numexpr/necompiler.py in evaluate(ex, local_dict, global_dict, out, order, casting, sanitize, _frame_depth, **kwargs)
    987                  _frame_depth=_frame_depth, sanitize=sanitize, **kwargs)
    988     if e is None:
--> 989         return re_evaluate(local_dict=local_dict, global_dict=global_dict, _frame_depth=_frame_depth)
    990     else:
    991         raise e

/usr/local/lib/python3.12/dist-packages/numexpr/necompiler.py in re_evaluate(local_dict, global_dict, _frame_depth)
   1020     kwargs = _numexpr_last.l['kwargs']
   1021     # with evaluate_lock:
-> 1022     return compiled_ex(*args, **kwargs)

ValueError: data type must provide an itemsize