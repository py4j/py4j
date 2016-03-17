/******************************************************************************
 * Copyright (c) 2009-2016, Barthelemy Dagenais and individual contributors.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - The name of the author may not be used to endorse or promote products
 * derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *****************************************************************************/
package py4j.examples;

public class UTFExample {

	private Byte[] array = new Byte[] { 0, 1, 10, 127, -1, -128 };

	public int strangeMéthod() {
		return 2;
	}

	public Byte[] getSurrogateBytes() {
		return new Byte[] { (byte) 0xD8, (byte) 0xD9, (byte) 0xDF };
	}

	public byte[] getSurrogatebytes() {
		return new byte[] { (byte) 0xD8, (byte) 0xD9, (byte) 0xDF };
	}

	public int getPositiveByteValue(byte b) {
		return (int) (b & 0xff);
	}

	public int getJavaByteValue(byte b) {
		return (int) b;
	}

	public int[] getUtfValue(String s) {
		int length = s.length();
		int[] values = new int[length];

		for (int i = 0; i < length; i++) {
			values[i] = s.charAt(i);
		}

		return values;
	}

	public int[] getBytesValue(byte[] bytes) {
		int length = bytes.length;
		int[] values = new int[length];

		for (int i = 0; i < length; i++) {
			values[i] = bytes[i] & 0xff;
		}

		return values;
	}

	public byte[] getBytesValue() {
		return new byte[] { 0, 1, 10, 127, -1, -128 };
	}

	public Byte[] getBytesArray() {
		return array;
	}
}
