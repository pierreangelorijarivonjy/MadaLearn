#!/usr/bin/env bash
# Design System Refactoring Checklist

# COMPLETED PAGES ✅
# 1. /dashboard/page.tsx - Dashboard with stats and role-based menu
# 2. /courses/page.tsx - Courses list with search and filters  
# 3. /library/page.tsx - Library with search and filters

# READY TO REFACTOR 🔄
# 4. /profile/page.tsx
# 5. /admin/users/page.tsx
# 6. /quizzes/page.tsx
# 7. /quizzes/[id]/page.tsx
# 8. /courses/[id]/page.tsx
# 9. /library/[id]/page.tsx
# 10. /courses/create/page.tsx
# 11. /library/create/page.tsx
# 12. /quizzes/create/page.tsx (already partial, needs polish)

# QUICK IMPLEMENTATION TEMPLATE
# ==============================
# 
# 1. Replace imports at top:
#    OLD: individual imports from lucide-react and components
#    NEW: import { PageLayout, PageHeader, Section, ... } from '@/components/ui'
#
# 2. Wrap return JSX in:
#    <PageLayout>
#      <PageHeader title="..." subtitle="..." />
#      <Section>...</Section>
#    </PageLayout>
#
# 3. Replace old cards with:
#    <Card><CardHeader>...</CardHeader><CardContent>...</CardContent></Card>
#
# 4. Replace old buttons with:
#    <Button variant="primary">Text</Button>
#
# 5. Replace old typography with:
#    <H1>, <H2>, <H3>, <H4>, <Text>, <SecondaryText>
#
# 6. Replace error divs with error card pattern from Courses/Library pages
#
# 7. Replace loading spinners with:
#    <SkeletonGrid count={8} /> or <SkeletonCard />
#
# 8. Replace empty states with:
#    <EmptyState icon={Icon} title="..." description="..." />
#
# PATTERN FILES TO REFERENCE:
# - /frontend/src/app/dashboard/page.tsx (Excellent reference)
# - /frontend/src/app/courses/page.tsx (List page pattern)
# - /frontend/src/app/library/page.tsx (List page pattern)
#
# FORMS PATTERN:
# - Use <FormInput label="..." icon={...} />
# - Use <FormSelect label="..." options={[...]} />
# - Use <FormTextarea label="..." rows={4} />
# - Wrap in <Card><CardHeader>...</CardHeader><CardContent>...</CardContent></Card>
#
# TABLE PATTERN:
# <Table>
#   <TableHead>
#     <TableRow>
#       <TableCell header>Column Name</TableCell>
#     </TableRow>
#   </TableHead>
#   <TableBody>
#     <TableRow>
#       <TableCell>Data</TableCell>
#     </TableRow>
#   </TableBody>
# </Table>
#
# READY TO START? Pick a page and:
# 1. Open the file
# 2. Check DESIGN_SYSTEM.md for component API
# 3. Reference completed pages for patterns
# 4. Follow the template above
# 5. Test with npm run build
# 6. Verify no TypeScript errors
#
# Questions? See:
# - /memories/session/design_system_guide.md (full guide)
# - /memories/session/implementation_complete.md (status report)
# - /frontend/DESIGN_SYSTEM.md (component docs)
