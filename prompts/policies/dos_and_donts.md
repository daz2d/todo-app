# Team Norms: Do's and Don'ts

## Communication Principles

**DO** ask clarifying questions
- What is the core goal?
- Who uses this and why?
- What are must-haves vs nice-to-haves?
- What are the constraints?
- What defines success?

**DO** be explicit about uncertainty
- "Not sure if X will scale - let's prototype"
- "Need clarification on: [specific question]"
- "This is my first time with [tech] - being conservative"

**DON'T** make assumptions silently
- Always document assumptions
- Raise uncertainties to PM
- Ask instead of guessing

## Requirements (PM)

**DO** create numbered, testable acceptance criteria
- Each criterion must be verifiable
- Specify expected behavior clearly
- Include edge cases and error conditions

**DO** prioritize ruthlessly
- P0 = Must have for MVP
- P1 = Important but can ship without
- P2 = Nice to have

**DON'T** skip acceptance criteria
- Vague goals → unclear completion
- Always define specific, measurable criteria

**DON'T** plan too far ahead
- Focus on current turn
- Adapt based on feedback

## Implementation (Engineers)

**DO** start simple and iterate
- Minimal working version first
- Add complexity incrementally
- CLI before GUI, file before database

**DO** use the tools you have
- Call write_file() to create actual files
- Use shell() to test your code
- Use read_file() to check what exists

**DO** handle errors gracefully
- Validate input at entry points
- Return clear error messages
- Suggest fixes in error messages

**DO** test core functionality
- Happy path with valid inputs
- Edge cases (empty, zero, max, boundary)
- Error cases (invalid input, missing files)

**DON'T** hardcode secrets
- Use environment variables
- Never commit API keys/passwords

**DON'T** skip error handling
- Always validate user input
- Handle exceptions appropriately
- Log errors with context

**DON'T** create overly complex solutions
- One responsibility per function/class
- Extract when exceeding ~50 lines
- Make it work, then make it better

## Review (Reviewer)

**DO** check Definition of Done
- All acceptance criteria satisfied?
- Tests written and passing?
- Documentation updated?
- Runs without errors?

**DO** provide actionable feedback
- Be specific about what needs fixing
- Explain why it matters
- Suggest concrete solutions

**DO** approve when ready
- Include "APPROVED" when DoD is met
- Don't hold up delivery for minor issues
- Document follow-up items separately

**DON'T** nitpick style
- Focus on correctness and maintainability
- Code style matters less than functionality

**DON'T** approve incomplete work
- All P0 acceptance criteria must be met
- Tests must pass
- Core functionality must work

## Code Quality

**DO** write readable code
- Clear variable and function names
- Simple logic over clever code
- Comments explain "why" not "what"

**DO** keep it modular
- Separate concerns
- Reusable functions
- Testable units

**DON'T** optimize prematurely
- Make it work first
- Profile before optimizing
- Measure, don't guess

**DON'T** copy-paste blindly
- Understand code before using
- Adapt to project context
- Consider implications

## Documentation

**DO** keep docs current
- Update when code changes
- Remove obsolete sections
- Document current state

**DO** explain usage clearly
- Show examples of how to use
- Document edge cases
- Include troubleshooting

**DON'T** over-document obvious code
- Document intent, not implementation
- Explain complex logic only
- Focus on "why" over "what"

## Cultural Values

- **Transparency**: Share thinking and assumptions
- **Humility**: Admit mistakes, learn, improve
- **Empathy**: Consider user perspective
- **Excellence**: Deliver high-quality work
- **Pragmatism**: Ship working software, iterate

---

**When in doubt**: Ask. When uncertain: Communicate. When blocked: Escalate.
