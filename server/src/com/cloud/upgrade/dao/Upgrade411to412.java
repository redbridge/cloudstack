// Licensed to the Apache Software Foundation (ASF) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The ASF licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

package com.cloud.upgrade.dao;

import com.cloud.utils.crypt.DBEncryptionUtil;
import com.cloud.utils.exception.CloudRuntimeException;
import com.cloud.utils.script.Script;
import org.apache.log4j.Logger;

import java.io.File;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class Upgrade411to412 implements DbUpgrade {
    final static Logger s_logger = Logger.getLogger(Upgrade410to411.class);

    @Override
    public String[] getUpgradableVersionRange() {
        return new String[] { "4.1.1", "4.1.2" };
    }

    @Override
    public String getUpgradedVersion() {
        return "4.1.2";
    }

    @Override
    public boolean supportsRollingUpgrade() {
        return false;
    }

    @Override
    public File[] getPrepareScripts() {
        // Do nothing.
        return null;
    }

    @Override
    public void performDataMigration(Connection conn) {
        // Nothing to be done.
    }

    @Override
    public File[] getCleanupScripts() {
        return null;
    }

}
