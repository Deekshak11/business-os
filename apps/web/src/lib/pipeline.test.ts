import { describe, expect, it } from "vitest";
import {
  selectPipelineStep,
  shouldAutoOpenPlan,
  suggestedViewForStep,
  stepIndex,
} from "./pipeline";

describe("selectPipelineStep (shipped helper)", () => {
  it("starts at context with empty session", () => {
    expect(
      selectPipelineStep({
        status: "chatting",
        awaitingApproval: false,
        hasUserMessage: false,
        hasPlan: false,
        hasExecution: false,
      }),
    ).toBe("context");
  });

  it("moves to strategy after user message", () => {
    expect(
      selectPipelineStep({
        status: "chatting",
        awaitingApproval: false,
        hasUserMessage: true,
        hasPlan: false,
        hasExecution: false,
      }),
    ).toBe("strategy");
  });

  it("plan_ready without approval flag → plan", () => {
    expect(
      selectPipelineStep({
        status: "plan_ready",
        awaitingApproval: false,
        hasUserMessage: true,
        hasPlan: true,
        hasExecution: false,
      }),
    ).toBe("plan");
  });

  it("awaiting approval → approve", () => {
    expect(
      selectPipelineStep({
        status: "plan_ready",
        awaitingApproval: true,
        hasUserMessage: true,
        hasPlan: true,
        hasExecution: false,
      }),
    ).toBe("approve");
  });

  it("execution handoff → execute then done", () => {
    expect(
      selectPipelineStep({
        status: "executing",
        awaitingApproval: false,
        hasUserMessage: true,
        hasPlan: true,
        hasExecution: true,
      }),
    ).toBe("execute");
    expect(
      selectPipelineStep({
        status: "done",
        awaitingApproval: false,
        hasUserMessage: true,
        hasPlan: true,
        hasExecution: true,
        executionComplete: true,
      }),
    ).toBe("done");
  });

  it("suggested views match product flow", () => {
    expect(suggestedViewForStep("strategy")).toBe("chat");
    expect(suggestedViewForStep("approve")).toBe("plan");
    expect(suggestedViewForStep("execute")).toBe("pipeline");
    expect(suggestedViewForStep("done")).toBe("outputs");
    expect(stepIndex("approve")).toBeGreaterThan(stepIndex("strategy"));
  });
});

describe("shouldAutoOpenPlan", () => {
  it("opens on awaiting_approval / plan_ready", () => {
    expect(
      shouldAutoOpenPlan({
        awaitingApproval: true,
        status: "chatting",
        reply: "ok",
        meatyPlan: true,
        hasPlan: true,
      }),
    ).toBe(true);
    expect(
      shouldAutoOpenPlan({
        awaitingApproval: false,
        status: "plan_ready",
        reply: "ok",
        meatyPlan: true,
        hasPlan: true,
      }),
    ).toBe(true);
  });

  it("opens when user asked for a mock plan and body is meaty (flag lag)", () => {
    expect(
      shouldAutoOpenPlan({
        awaitingApproval: false,
        status: "chatting",
        reply: "Here is a full strategy with steps…",
        meatyPlan: true,
        hasPlan: true,
        userMessage: "generate a mock plan for my agency",
      }),
    ).toBe(true);
  });

  it("opens on mock data phrasing even with thin meat when hasPlan", () => {
    expect(
      shouldAutoOpenPlan({
        awaitingApproval: false,
        status: "chatting",
        reply: "Mock plan for a gym SaaS…",
        meatyPlan: false,
        hasPlan: true,
        userMessage: "create mock data and show me the plan",
      }),
    ).toBe(true);
  });

  it("opens whenever plan is meaty", () => {
    expect(
      shouldAutoOpenPlan({
        awaitingApproval: false,
        status: "chatting",
        reply: "Here's the diagnosis…",
        meatyPlan: true,
        hasPlan: true,
      }),
    ).toBe(true);
  });

  it("does not open without a plan", () => {
    expect(
      shouldAutoOpenPlan({
        awaitingApproval: true,
        status: "plan_ready",
        reply: "x",
        meatyPlan: false,
        hasPlan: false,
      }),
    ).toBe(false);
  });

  it("does not open mid-coaching with thin plan and no flags", () => {
    expect(
      shouldAutoOpenPlan({
        awaitingApproval: false,
        status: "chatting",
        reply: "What is your offer?",
        meatyPlan: false,
        hasPlan: true,
        userMessage: "I sell automations",
      }),
    ).toBe(false);
  });
});
