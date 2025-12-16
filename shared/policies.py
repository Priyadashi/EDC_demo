"""
Policy Engine - Evaluates ODRL-based policies for data access control.

This module provides automotive-specific policy templates and a policy
evaluator that determines if access should be granted based on the
consumer's attributes and the policy constraints.
"""

from typing import Any, Optional
from .models import Policy, Permission, Prohibition, Constraint, PolicyEvaluationResult


class PolicyEvaluator:
    """
    Evaluates policies against a context to determine access rights.

    The context contains attributes about the requesting party, such as:
    - partner_type: "tier1_supplier", "tier2_supplier", "oem", etc.
    - region: "EU", "NA", "APAC"
    - certification: ["ISO27001", "TISAX", "IATF16949"]
    - purpose: "quality_analysis", "production_planning", etc.
    """

    def evaluate(self, policy: Policy, context: dict) -> PolicyEvaluationResult:
        """
        Evaluate if access should be granted based on policy and context.

        Args:
            policy: The policy to evaluate
            context: Attributes of the requesting party

        Returns:
            PolicyEvaluationResult with allowed status and reason
        """
        evaluated_constraints = []

        # First, check prohibitions (deny rules)
        for prohibition in policy.prohibitions:
            if self._action_matches(prohibition.action, context.get("action", "USE")):
                constraint_results = self._evaluate_constraints(prohibition.constraints, context)
                if all(r["satisfied"] for r in constraint_results):
                    return PolicyEvaluationResult(
                        allowed=False,
                        reason=f"Action '{prohibition.action}' is prohibited",
                        evaluated_constraints=constraint_results
                    )
                evaluated_constraints.extend(constraint_results)

        # Then, check permissions (allow rules)
        for permission in policy.permissions:
            if self._action_matches(permission.action, context.get("action", "USE")):
                if not permission.constraints:
                    # No constraints means permission is granted
                    return PolicyEvaluationResult(
                        allowed=True,
                        reason="Permission granted (no constraints)",
                        evaluated_constraints=evaluated_constraints
                    )

                constraint_results = self._evaluate_constraints(permission.constraints, context)
                evaluated_constraints.extend(constraint_results)

                if all(r["satisfied"] for r in constraint_results):
                    return PolicyEvaluationResult(
                        allowed=True,
                        reason="All permission constraints satisfied",
                        evaluated_constraints=evaluated_constraints
                    )

        # Default deny if no permission matched
        return PolicyEvaluationResult(
            allowed=False,
            reason="No matching permission found",
            evaluated_constraints=evaluated_constraints
        )

    def _action_matches(self, policy_action: str, request_action: str) -> bool:
        """Check if the requested action matches the policy action."""
        return policy_action.upper() == request_action.upper()

    def _evaluate_constraints(self, constraints: list[Constraint], context: dict) -> list[dict]:
        """Evaluate a list of constraints against the context."""
        results = []
        for constraint in constraints:
            satisfied = self._evaluate_single_constraint(constraint, context)
            results.append({
                "constraint": f"{constraint.left_operand} {constraint.operator} {constraint.right_operand}",
                "context_value": context.get(constraint.left_operand, "NOT_PROVIDED"),
                "satisfied": satisfied
            })
        return results

    def _evaluate_single_constraint(self, constraint: Constraint, context: dict) -> bool:
        """Evaluate a single constraint."""
        left_value = context.get(constraint.left_operand)
        right_value = constraint.right_operand
        operator = constraint.operator.lower()

        if left_value is None:
            return False

        if operator == "eq":
            return left_value == right_value
        elif operator == "neq":
            return left_value != right_value
        elif operator == "in":
            if isinstance(right_value, list):
                return left_value in right_value
            return False
        elif operator == "gt":
            return left_value > right_value
        elif operator == "lt":
            return left_value < right_value
        elif operator == "gte":
            return left_value >= right_value
        elif operator == "lte":
            return left_value <= right_value
        elif operator == "contains":
            if isinstance(left_value, list):
                return right_value in left_value
            return right_value in str(left_value)
        elif operator == "has_any":
            # Check if left_value (list) has any item from right_value (list)
            if isinstance(left_value, list) and isinstance(right_value, list):
                return bool(set(left_value) & set(right_value))
            return False

        return False


# Pre-defined automotive policy templates

TIER1_SUPPLIER_ONLY_POLICY = Policy(
    id="policy-tier1-only",
    permissions=[
        Permission(
            action="USE",
            constraints=[
                Constraint(
                    leftOperand="partner_type",
                    operator="eq",
                    rightOperand="tier1_supplier"
                )
            ]
        )
    ],
    prohibitions=[
        Prohibition(action="DISTRIBUTE")
    ]
)

CERTIFIED_PARTNERS_POLICY = Policy(
    id="policy-certified-partners",
    permissions=[
        Permission(
            action="USE",
            constraints=[
                Constraint(
                    leftOperand="certification",
                    operator="has_any",
                    rightOperand=["TISAX", "ISO27001"]
                )
            ]
        )
    ],
    prohibitions=[
        Prohibition(action="DISTRIBUTE"),
        Prohibition(action="MODIFY")
    ]
)

EU_REGION_POLICY = Policy(
    id="policy-eu-region",
    permissions=[
        Permission(
            action="USE",
            constraints=[
                Constraint(
                    leftOperand="region",
                    operator="in",
                    rightOperand=["EU", "EEA"]
                )
            ]
        )
    ],
    prohibitions=[
        Prohibition(action="DISTRIBUTE")
    ]
)

QUALITY_DATA_POLICY = Policy(
    id="policy-quality-data",
    permissions=[
        Permission(
            action="USE",
            constraints=[
                Constraint(
                    leftOperand="partner_type",
                    operator="in",
                    rightOperand=["tier1_supplier", "tier2_supplier"]
                ),
                Constraint(
                    leftOperand="purpose",
                    operator="eq",
                    rightOperand="quality_analysis"
                )
            ]
        )
    ],
    prohibitions=[
        Prohibition(action="DISTRIBUTE"),
        Prohibition(action="ARCHIVE")
    ],
    obligations=[
        # Note: Obligations are informational in this demo
    ]
)

TRACEABILITY_POLICY = Policy(
    id="policy-traceability",
    permissions=[
        Permission(
            action="USE",
            constraints=[
                Constraint(
                    leftOperand="certification",
                    operator="contains",
                    rightOperand="IATF16949"
                )
            ]
        )
    ],
    prohibitions=[]
)

OPEN_ACCESS_POLICY = Policy(
    id="policy-open-access",
    permissions=[
        Permission(action="USE", constraints=[])
    ],
    prohibitions=[
        Prohibition(action="DISTRIBUTE")
    ]
)


# Map of policy IDs to policy objects
POLICY_TEMPLATES = {
    "tier1-only": TIER1_SUPPLIER_ONLY_POLICY,
    "certified-partners": CERTIFIED_PARTNERS_POLICY,
    "eu-region": EU_REGION_POLICY,
    "quality-data": QUALITY_DATA_POLICY,
    "traceability": TRACEABILITY_POLICY,
    "open-access": OPEN_ACCESS_POLICY,
}


def get_policy_description(policy: Policy) -> str:
    """Generate a human-readable description of a policy."""
    descriptions = []

    for perm in policy.permissions:
        perm_desc = f"Allows {perm.action}"
        if perm.constraints:
            constraints_desc = []
            for c in perm.constraints:
                constraints_desc.append(f"{c.left_operand} {c.operator} {c.right_operand}")
            perm_desc += f" when: {' AND '.join(constraints_desc)}"
        descriptions.append(perm_desc)

    for prohib in policy.prohibitions:
        descriptions.append(f"Prohibits {prohib.action}")

    return "; ".join(descriptions) if descriptions else "No restrictions"
