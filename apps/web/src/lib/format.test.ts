import { describe, expect, it } from "vitest";
import {
  displayField,
  formatConstraint,
  formatRoute,
  formatStage,
  isEmptyValue,
} from "./format";

describe("format helpers", () => {
  it("formats stages with names", () => {
    expect(formatStage("0")).toContain("Improvise");
    expect(formatStage("2")).toContain("Advertise");
    expect(formatStage("unknown")).toBe("Not set");
  });

  it("hides none routes", () => {
    expect(formatRoute("none")).toBeNull();
    expect(formatRoute("copy")).toBe("Copywriting Agent");
    expect(formatRoute("both")).toBe("Copywriting + Builder");
  });

  it("detects empty / unknown offer text", () => {
    expect(isEmptyValue("unknown — no paid offer described")).toBe(true);
    expect(isEmptyValue("Coaching package")).toBe(false);
    expect(displayField("unknown")).toBe("Not provided yet");
  });

  it("title-cases constraints", () => {
    expect(formatConstraint("product")).toBe("Product");
    expect(formatConstraint("unknown")).toBe("Not set");
  });
});
