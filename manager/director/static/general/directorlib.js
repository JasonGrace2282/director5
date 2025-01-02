/**
 * Director5 shared javascript library
 */

const version = "v1.0.0";

class DirectorLibError extends Error {
	constructor(message = "") {
		super(message);
	}
}

class Director {
	static getVersion() {
		return version;
	}
}
