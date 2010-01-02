/**
 * Copyright (c) 2009, 2010, Barthelemy Dagenais All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
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
 */

package py4j;

public class ReturnObject {

	private String name;
	private Object primitiveObject;
	private boolean isReference;
	private boolean isMap;
	private boolean isList;
	private boolean isNull;
	private boolean isError;
	private int size;

	private ReturnObject() {
	}

	public static ReturnObject getListReturnObject(String name, int size) {
		ReturnObject rObject = new ReturnObject();
		rObject.name = name;
		rObject.size = size;
		rObject.isList = true;
		return rObject;
	}
	
	public static ReturnObject getPrimitiveReturnObject(Object primitive) {
		ReturnObject rObject = new ReturnObject();
		rObject.primitiveObject = primitive;
		return rObject;
	}
	
	public static ReturnObject getReferenceReturnObject(String name) {
		ReturnObject rObject = new ReturnObject();
		rObject.name = name;
		rObject.isReference = true;
		return rObject;
	}
	
	public static ReturnObject getNullReturnObject() {
		ReturnObject rObject = new ReturnObject();
		rObject.isNull = true;
		return rObject;
	}
	
	public static ReturnObject getErrorReturnObject() {
		ReturnObject rObject = new ReturnObject();
		rObject.isError = true;
		return rObject;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public boolean isMap() {
		return isMap;
	}

	public void setMap(boolean isMap) {
		this.isMap = isMap;
	}

	public boolean isList() {
		return isList;
	}

	public void setList(boolean isList) {
		this.isList = isList;
	}

	public int getSize() {
		return size;
	}

	public void setSize(int size) {
		this.size = size;
	}

	public boolean isNull() {
		return isNull;
	}

	public void setNull(boolean isNull) {
		this.isNull = isNull;
	}

	public boolean isError() {
		return isError;
	}

	public void setError(boolean isError) {
		this.isError = isError;
	}

	public Object getPrimitiveObject() {
		return primitiveObject;
	}

	public void setPrimitiveObject(Object primitiveObject) {
		this.primitiveObject = primitiveObject;
	}

	public boolean isReference() {
		return isReference;
	}

	public void setReference(boolean isReference) {
		this.isReference = isReference;
	}

	
	
}
