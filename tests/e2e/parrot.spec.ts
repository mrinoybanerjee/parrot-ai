import { expect, test } from "@playwright/test";

test("completes a typed conversation turn", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Parrot-AI" })).toBeVisible();
  await expect(page.getByLabel("Target language")).toBeVisible();
  await expect(page.getByText("Learning Coach")).toBeVisible();

  await page.getByLabel("Your response").fill("Tengo alergias y necesito una medicina.");
  await page.getByRole("button", { name: "Send" }).click();

  await expect(
    page.getByLabel("Conversation messages").getByText("Tengo alergias y necesito una medicina.", {
      exact: true,
    }),
  ).toBeVisible();
  await expect(page.getByText("Repair")).toBeVisible();
  await expect(page.getByText("Phrase bank")).toBeVisible();
  await expect(page.getByLabel("Phrase bank").getByText("Can I explain the situation first?")).toBeVisible();
});

test("mobile layout keeps the workspace usable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Parrot-AI" })).toBeVisible();
  await expect(page.getByLabel("Situation")).toBeVisible();
  await expect(page.getByLabel("Your response")).toBeVisible();
});
