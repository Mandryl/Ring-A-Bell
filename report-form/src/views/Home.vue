<template>
  <div class="home">
    <el-container
    v-loading="loading"
    element-loading-text="Sending..."
    :element-loading-spinner="svg"
    element-loading-svg-view-box="-10, -10, 50, 50"
    element-loading-background="rgba(0, 0, 0, 0.8)"
    >
      <el-header class="header">
        <img src="../assets/Ring_A_Bell_logo.png" class="header-image" />
        <h1>Ring A Bell</h1>
      </el-header>
      <el-main class="main-content">
        <el-form
          ref="form"
          :model="form"
          label-width="120px"
          label-position="top"
        >
          <el-form-item label="Your name" :required="!form.anonymous">
            <el-input v-model="form.name" :disabled="form.anonymous"></el-input>
          </el-form-item>
          <el-form-item label="Anonymity">
            <el-switch class="form-switch" v-model="form.anonymous" ></el-switch>
          </el-form-item>
          <span v-if="form.anonymous">Your report will be send anonymously.</span>
          <el-form-item label="Your Problem and Trouble" required>
            <el-input v-model="form.problem" :rows="10" type="textarea" />
          </el-form-item>
          <el-form-item>
            <el-button class="send-button" type="primary" @click="onSubmit"
              >Send Report</el-button
            >
          </el-form-item>
        </el-form>
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: "Home",
  components: {},
  data: () => ({
    loading:false,
    form: {
      name: "",
      problem: "",
      anonymous:false
    },
    url:"http://trouble-api-vol1003-dev.apps.sandbox-m2.ll9k.p1.openshiftapps.com/troubles"
  }),
  methods: {
    onSubmit(){
      const name = (this.form.anonymous)? "anonymous": this.form.name;
      const problem = this.form.problem;
      this.loading = true;
      this.axios.post(this.url,{
        student_name:name,
        description:problem,
        summary:problem,
        comments:[],
        id:"P"+Date.now(),
        status:"Open"
      }).then((res)=>{
        this.loading = false;
      }).catch((error)=>{
        this.loading = false;
      });
    }
  }
};
</script>

<style>
.header {
  height: 10vh;
  width: 100vw;
  display: inline-flex;
  background-color: white;
  justify-content: start;
}
.header-image {
  height: 100%;
  margin-right: 5px;
}

.header h1 {
  margin-left: 5px;
}
.send-button {
  width: 80vw;
}

.form-switch{
  display: flex!important;
  justify-content: left;
}
</style>
