# Implementation Plan

- [ ] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - QdrantClient Search Method AttributeError
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: For deterministic bugs, scope the property to the concrete failing case(s) to ensure reproducibility
  - Test that search_similar() calls with valid embeddings fail with AttributeError on unfixed code
  - Test that ClipSearchService.search_by_text() fails with AttributeError on unfixed code
  - Test that API endpoint /api/answer_key_generator fails with 500 error on unfixed code
  - The test assertions should match the Expected Behavior Properties from design
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found to understand root cause
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Non-Search Operations Behavior
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs (image indexing, direct similarity, collection management)
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Test that ClipSearchService.index_images() continues to work correctly
  - Test that ClipSearchService.get_direct_similarity() produces same results
  - Test that collection management operations continue working
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 3. Fix QdrantClient search method usage in imageRag.py

  - [ ] 3.1 Implement the fix
    - Replace deprecated client.search() with client.query_points() in QdrantManager.search_similar()
    - Update parameter mapping: query_vector → query parameter
    - Maintain collection_name, limit, with_payload, with_vectors parameters
    - Follow the same pattern used in ragProcessor.py and qdrantManager.py
    - Ensure return format matches what calling code expects
    - _Bug_Condition: isBugCondition(input) where input.operation == "search_similar" AND currentImplementation.uses("client.search()")_
    - _Expected_Behavior: expectedBehavior(result) from design - successful vector similarity search using query_points() API_
    - _Preservation: Preservation Requirements from design - image indexing, direct similarity, collection management unchanged_
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3_

  - [ ] 3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - QdrantClient Search Method Success
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: Expected Behavior Properties from design_

  - [ ] 3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - Non-Search Operations Behavior
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)

- [ ] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.