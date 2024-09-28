import { nestObject } from "../util.js";

describe("nestObject", () => {
  it("should handle empty object", () => {
    expect(nestObject({})).toEqual({});
  });

  it("should handle simple key-value pairs", () => {
    const flatObject = {
      name: "John Doe",
      age: 30,
    };
    const expectedNestedObject = {
      name: "John Doe",
      age: 30,
    };
    expect(nestObject(flatObject)).toEqual(expectedNestedObject);
  });

  it("should handle nested objects", () => {
    const flatObject = {
      "user.name": "John Doe",
      "user.age": 30,
      "address.street": "123 Main St",
      "address.city": "Anytown",
    };
    const expectedNestedObject = {
      user: {
        name: "John Doe",
        age: 30,
      },
      address: {
        street: "123 Main St",
        city: "Anytown",
      },
    };
    expect(nestObject(flatObject)).toEqual(expectedNestedObject);
  });

  it("should handle arrays", () => {
    const flatObject = {
      "items[0]": "apple",
      "items[1]": "banana",
      "items[2]": "orange",
    };
    const expectedNestedObject = {
      items: ["apple", "banana", "orange"],
    };
    expect(nestObject(flatObject)).toEqual(expectedNestedObject);
  });

  it("should handle nested objects and arrays", () => {
    const flatObject = {
      "user.name": "John Doe",
      "user.hobbies[0]": "reading",
      "user.hobbies[1]": "coding",
      "address.street": "123 Main St",
      "address.city": "Anytown",
    };
    const expectedNestedObject = {
      user: {
        name: "John Doe",
        hobbies: ["reading", "coding"],
      },
      address: {
        street: "123 Main St",
        city: "Anytown",
      },
    };
    expect(nestObject(flatObject)).toEqual(expectedNestedObject);
  });

  it("should handle keys with '.' in quotes", () => {
    const flatObject = {
      "user.'first.name'": "John",
      "user.'last.name'": "Doe",
    };
    const expectedNestedObject = {
      user: {
        "first.name": "John",
        "last.name": "Doe",
      },
    };
    expect(nestObject(flatObject)).toEqual(expectedNestedObject);
  });

  it("should handle sparse arrays", () => {
    const flatObject = {
      "items[0]": "apple",
      "items[2]": "orange",
    };
    const expectedNestedObject = {
      items: ["apple", null, "orange"],
    };
    expect(nestObject(flatObject)).toEqual(expectedNestedObject);
  });

  it("should handle arrays as object values", () => {
    const flatObject = {
      "user.name": "John Doe",
      "user.roles[0]": "admin",
      "user.roles[1]": "user",
    };
    const expectedNestedObject = {
      user: {
        name: "John Doe",
        roles: ["admin", "user"],
      },
    };
    expect(nestObject(flatObject)).toEqual(expectedNestedObject);
  });

  it("should handle nested objects and arrays with custom delimiter", () => {
    const flatObject = {
      "user|name": "John Doe",
      "user|hobbies[0]": "reading",
      "user|hobbies[1]": "coding",
      "address|street": "123 Main St",
      "address|city": "Anytown",
    };
    const expectedNestedObject = {
      user: {
        name: "John Doe",
        hobbies: ["reading", "coding"],
      },
      address: {
        street: "123 Main St",
        city: "Anytown",
      },
    };
    expect(nestObject(flatObject, "|")).toEqual(expectedNestedObject);
  });

  it("should handle keys with delimiter in quotes", () => {
    const flatObject = {
      "user.'first.name'": "John",
      "user.'last.name'": "Doe",
    };
    const expectedNestedObject = {
      user: {
        "first.name": "John",
        "last.name": "Doe",
      },
    };
    expect(nestObject(flatObject, ".")).toEqual(expectedNestedObject);
  });

  it("should handle nested arrays", () => {
    const flatObject = {
      "items[0][0]": "apple",
      "items[0][1]": "banana",
      "items[1][0]": "orange",
    };
    const expectedNestedObject = {
      items: [["apple", "banana"], ["orange"]],
    };
    expect(nestObject(flatObject)).toEqual(expectedNestedObject);
  });

  it("should handle nested arrays key reference", () => {
    const flatObject = {
      "items[0][1].fruits": "apple",
      "items[0][1].flower": "lotus",
      "items[0][0].fruits": "orange",
      "items[1][0].fruits": "banana",
    };
    const expectedNestedObject = {
      items: [
        [
          {
            fruits: "orange",
          },
          {
            fruits: "apple",
            flower: "lotus",
          },
        ],
        [
          {
            fruits: "banana",
          },
        ],
      ],
    };
    expect(nestObject(flatObject)).toEqual(expectedNestedObject);
  });
});
