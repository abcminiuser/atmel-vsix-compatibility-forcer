'''
            Atmel Studio Extension Compatibility Forcer.

    By Dean Camera (dean [at] fourwalledcubicle [dot] com)
    Released into the public domain.


    This script will force a given Visual Studio 2010 extension to be marked as
    being compatible with a given version of Atmel Studio. THIS DOES NOT ENSURE
    THE RESULTING EXTENSION WILL WORK CORRECTLY, and should only be used on
    extensions that rely on the core Visual Studio infrastructure (such as
    extensions from the Visual Studio gallery that add new editor features) or
    on known-good extensions that have not had their manifest files updated.

    Use of this script and modified extensions is AT YOUR OWN RISK.
'''

import sys
import os
import re
from zipfile import ZipFile
import xml.etree.ElementTree as ET

vsix_namespace_map = {'vsix' : 'http://schemas.microsoft.com/developer/vsx-schema/2010'}
ET.register_namespace('', 'http://schemas.microsoft.com/developer/vsx-schema/2010')

def add_supported_product(tree, type, version, name):
    references = tree.find(".//vsix:References", namespaces=vsix_namespace_map)
    references.clear()

    supported_products = tree.find(".//vsix:SupportedProducts", namespaces=vsix_namespace_map)

    new_supported_product = ET.SubElement(supported_products, "%s" % type)
    new_supported_product.set('Version', str(version))
    new_supported_product.text = name

def make_as_compatible(input_vsix_file, desired_version):
    # Input VSIX file without extension
    input_vsix_name = os.path.splitext(os.path.basename(vsix_file))[0]
    # Temporary folder where the extracted extension contents will be stored
    temp_folder_name = "%s_temp" % input_vsix_name
    # Input extension manifest file path
    extension_manifest = "%s/extension.vsixmanifest" % temp_folder_name
    # Output VSIX file name
    output_vsix_file = "%s_AtmelStudio%s.vsix" % (input_vsix_name, desired_version)

    # Extract input extension to a temporary directory
    with ZipFile(vsix_file, 'r') as vsix_zip:
        vsix_zip.extractall(temp_folder_name)

    # Add the Atmel Studio supported product to the manifest
    vsix_manifest_tree = ET.parse(extension_manifest)
    add_supported_product(vsix_manifest_tree, 'IsolatedShell', desired_version, "AtmelStudio")
    vsix_manifest_tree.write(extension_manifest)

    # Write the updated extension to a new VSIX file
    with ZipFile(output_vsix_file, 'w') as vsix_zip:
        for base, dirs, files in os.walk(temp_folder_name):
           for file in files:
              fn = os.path.join(base, file)
              vsix_zip.write(fn, os.path.relpath(fn, temp_folder_name))


if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print("Usage:   python make-as-compatible.py {Input}.vsix {Version}")
        print("Example: python make-as-compatible.py generic_extension.vsix 6.1")
        sys.exit(1)

    vsix_file = sys.argv[1]
    desired_version = sys.argv[2]

    if not os.path.isfile(sys.argv[1]):
        print("Input extension file is not valid.")
        sys.exit(1)

    if re.match("^\d.\d$", desired_version) is None:
        print("Desired version number is not valid.")
        sys.exit(1)

    make_as_compatible(vsix_file, desired_version)

    print("Extension compatibility forced to Atmel Studio %s." % desired_version)
