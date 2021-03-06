/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package com.cloud.hypervisor.xen.resource;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import javax.ejb.Local;

import org.apache.log4j.Logger;
import org.apache.xmlrpc.XmlRpcException;

import com.xensource.xenapi.Connection;
import com.xensource.xenapi.Types;
import com.xensource.xenapi.VM;
import com.xensource.xenapi.Host;

import org.apache.cloudstack.hypervisor.xenserver.XenServerResourceNewBase;

import com.cloud.resource.ServerResource;
import com.cloud.storage.resource.StorageSubsystemCommandHandler;
import com.cloud.storage.resource.StorageSubsystemCommandHandlerBase;
import com.cloud.utils.exception.CloudRuntimeException;
import com.cloud.utils.script.Script;
import com.cloud.utils.ssh.SSHCmdHelper;

@Local(value=ServerResource.class)
public class Xenserver625Resource extends XenServerResourceNewBase {
    private static final Logger s_logger = Logger.getLogger(Xenserver625Resource.class);

    public Xenserver625Resource() {
        super();
    }

    @Override
    protected String getGuestOsType(String stdType, boolean bootFromCD) {
        return CitrixHelper.getXenServer625GuestOsType(stdType, bootFromCD);
    }

    @Override
    protected List<File> getPatchFiles() {
        List<File> files = new ArrayList<File>();
        String patch = "scripts/vm/hypervisor/xenserver/xenserver62/patch";
        String patchfilePath = Script.findScript("", patch);
        if (patchfilePath == null) {
            throw new CloudRuntimeException("Unable to find patch file " + patch);
        }
        File file = new File(patchfilePath);
        files.add(file);
        return files;
    }

    @Override
    public long getStaticMax(String os, boolean b, long dynamicMinRam, long dynamicMaxRam){
        long recommendedValue = CitrixHelper.getXenServer625StaticMax(os, b);
        if(recommendedValue == 0){
            s_logger.warn("No recommended value found for dynamic max, setting static max and dynamic max equal");
            return dynamicMaxRam;
        }
        long staticMax = Math.min(recommendedValue, 4l * dynamicMinRam);  // XS constraint for stability
        if (dynamicMaxRam > staticMax){ // XS contraint that dynamic max <= static max
            s_logger.warn("dynamixMax " + dynamicMaxRam + " cant be greater than static max " + staticMax + ", can lead to stability issues. Setting static max as much as dynamic max ");
            return dynamicMaxRam;
        }
        return staticMax;
    }

    @Override
    public long getStaticMin(String os, boolean b, long dynamicMinRam, long dynamicMaxRam){
        long recommendedValue = CitrixHelper.getXenServer625StaticMin(os, b);
        if(recommendedValue == 0){
            s_logger.warn("No recommended value found for dynamic min");
            return dynamicMinRam;
        }

        if(dynamicMinRam < recommendedValue){   // XS contraint that dynamic min > static min
            s_logger.warn("Vm is set to dynamixMin " + dynamicMinRam + " less than the recommended static min " + recommendedValue + ", could lead to stability issues");
        }
        return dynamicMinRam;
    }

    @Override
    protected StorageSubsystemCommandHandler getStorageHandler() {
        XenServerStorageProcessor processor = new Xenserver625StorageProcessor(this);
        return new StorageSubsystemCommandHandlerBase(processor);
    }

    @Override
    protected void umountSnapshotDir(Connection conn, Long dcId) {

    }

    @Override
    protected boolean setupServer(Connection conn,Host host) {
        com.trilead.ssh2.Connection sshConnection = new com.trilead.ssh2.Connection(_host.ip, 22);
        try {
            sshConnection.connect(null, 60000, 60000);
            if (!sshConnection.authenticateWithPassword(_username, _password.peek())) {
                throw new CloudRuntimeException("Unable to authenticate");
            }

            String cmd = "rm -f /opt/xensource/sm/hostvmstats.py " +
                         "/opt/xensource/bin/copy_vhd_to_secondarystorage.sh " +
                         "/opt/xensource/bin/copy_vhd_from_secondarystorage.sh " +
                         "/opt/xensource/bin/create_privatetemplate_from_snapshot.sh " +
                         "/opt/xensource/bin/vhd-util " +
                         "/opt/cloud/bin/copy_vhd_to_secondarystorage.sh " +
                         "/opt/cloud/bin/copy_vhd_from_secondarystorage.sh " +
                         "/opt/cloud/bin/create_privatetemplate_from_snapshot.sh " +
                         "/opt/cloud/bin/vhd-util";

            SSHCmdHelper.sshExecuteCmd(sshConnection, cmd);
        } catch (Exception e) {
            s_logger.debug("Catch exception " + e.toString(), e);
        } finally {
            sshConnection.close();
        }
        return super.setupServer(conn, host);
    }

    @Override
    protected String revertToSnapshot(Connection conn, VM vmSnapshot,
                                      String vmName, String oldVmUuid, Boolean snapshotMemory, String hostUUID)
            throws Types.XenAPIException, XmlRpcException {

        String results = callHostPluginAsync(conn, "vmopsSnapshot",
                "revert_memory_snapshot", 10 * 60 * 1000, "snapshotUUID",
                vmSnapshot.getUuid(conn), "vmName", vmName, "oldVmUuid",
                oldVmUuid, "snapshotMemory", snapshotMemory.toString(), "hostUUID", hostUUID);
        String errMsg = null;
        if (results == null || results.isEmpty()) {
            errMsg = "revert_memory_snapshot return null";
        } else {
            if (results.equals("0")) {
                return results;
            } else {
                errMsg = "revert_memory_snapshot exception";
            }
        }
        s_logger.warn(errMsg);
        throw new CloudRuntimeException(errMsg);
    }

}
