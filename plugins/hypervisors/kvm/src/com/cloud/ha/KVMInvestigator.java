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
package com.cloud.ha;

import com.cloud.agent.AgentManager;
import com.cloud.agent.api.Answer;
import com.cloud.agent.api.CheckOnHostAnswer;
import com.cloud.agent.api.CheckOnHostCommand;
import com.cloud.host.HostVO;
import com.cloud.host.Status;
import com.cloud.host.dao.HostDao;
import com.cloud.hypervisor.Hypervisor.HypervisorType;
import com.cloud.resource.ResourceManager;
import com.cloud.utils.component.AdapterBase;
import com.cloud.vm.VMInstanceVO;
import org.apache.log4j.Logger;

import javax.ejb.Local;
import javax.inject.Inject;
import java.util.List;

@Local(value=Investigator.class)
public class KVMInvestigator extends AdapterBase implements Investigator {
    private final static Logger s_logger = Logger.getLogger(KVMInvestigator.class);
    @Inject
    HostDao _hostDao;
    @Inject
    AgentManager _agentMgr;
    @Inject
    ResourceManager _resourceMgr;
    @Override
    public Boolean isVmAlive(VMInstanceVO vm, HostVO host) {
        s_logger.debug("isVmAlive? vm: " + vm + " host: " + host);
        Status status = isAgentAlive(host);
        if (status == null) {
            return null;
        }
        return status == Status.Up ? true : null;
    }

    @Override
    public Status isAgentAlive(HostVO agent) {
        s_logger.debug("Checking agent " + agent);
        if (agent.getHypervisorType() != HypervisorType.KVM) {
            s_logger.debug("Host is not a KVM host");
            return null;
        }
        CheckOnHostCommand cmd = new CheckOnHostCommand(agent);
        List<HostVO> neighbors = _resourceMgr.listAllHostsInCluster(agent.getClusterId());
        for (HostVO neighbor : neighbors) {
            s_logger.debug("Investigation, agent " + agent + " from " + neighbor);
            if (neighbor.getId() == agent.getId() || neighbor.getHypervisorType() != HypervisorType.KVM) {
                s_logger.debug("Can't investigate using self");
                continue;
            }
            Answer answer = _agentMgr.easySend(neighbor.getId(), cmd);
            if (answer != null && answer.getResult()) {
                CheckOnHostAnswer ans = (CheckOnHostAnswer)answer;
                if (!ans.isDetermined()) {
                    s_logger.debug("Host " + neighbor + " couldn't determine the status of " + agent);
                    continue;
                }
                s_logger.debug("Returning status");
                return ans.isAlive() ? Status.Up : Status.Down;
            }

        }
        s_logger.debug("Unable to return status for " + agent);
        return null;
    }
}
